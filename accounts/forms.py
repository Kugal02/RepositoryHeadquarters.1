from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser
from agency.models import County
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from agency.models import UserProfile


class CustomUserSignupForm(UserCreationForm):
    USER_TYPE_CHOICES = [
        ('provider', 'Provider Agency'),
        ('coordinator', 'State/County Entity'),
    ]
    print(">>> SIGNUP VIEW CALLED <<<")

    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        widget=forms.RadioSelect,
        label="User Type",
        required=True,
    )

    state = forms.ChoiceField(
        choices=[
            ('OR', 'Oregon'),
        ],
        widget=forms.Select,
        label="State",
        initial='OR',
        required=True,
    )

    counties = forms.ModelMultipleChoiceField(
        queryset=County.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Counties"
    )

    agree_to_terms = forms.BooleanField(
        required=True,
        label="I agree to the Terms of Service"
    )

    profile_image = forms.ImageField(required=False, label="Profile Image")

    entity_type = forms.ChoiceField(
        choices=[('', 'Select Entity Type'), ('odds', 'ODDS'), ('vr', 'VR')],
        required=False,
        label="Entity Type (if State/County Entity)",
    )

    contact_first_name = forms.CharField(required=False, label="Contact First Name")
    contact_last_name = forms.CharField(required=False, label="Contact Last Name")
    contact_phone_number = forms.CharField(required=False, label="Contact Phone")
    contact_email = forms.EmailField(required=False, label="Contact Email")
    contact_address = forms.CharField(required=False, label="Contact Address or Office Location")
    job_title = forms.CharField(required=False, label="Job Title")
    agency_name = forms.CharField(required=False, label="Agency Name")

    class Meta:
        model = CustomUser
        fields = ('email', 'password1', 'password2', 'user_type', 'state', 'counties',
                  'entity_type', 'contact_phone_number',
                  'contact_email', 'contact_address', 'job_title', 'agency_name', 'agree_to_terms')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['counties'].queryset = County.objects.all()
        self.fields['email'].required = False
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Email'
        })

    def clean_agree_to_terms(self):
        agreed = self.cleaned_data.get('agree_to_terms')
        if not agreed:
            raise forms.ValidationError("You must agree to the terms to sign up.")
        return agreed

    def clean_profile_image(self):
        image = self.cleaned_data.get('profile_image')
        if image:
            # Check that the uploaded file is an image
            file_type = image.content_type.split('/')[0]
            if file_type != 'image':
                raise ValidationError('Only image files are allowed.')
        return image

    def clean_user_type(self):
        user_type = self.cleaned_data.get('user_type')
        if not user_type:
            raise forms.ValidationError("Please select a user type.")
        return user_type

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get("user_type")

        if user_type == "provider":
            # Provider must have agency_name
            if not cleaned_data.get("agency_name"):
                self.add_error("agency_name", "Agency name is required for providers.")
        elif user_type == "coordinator":
            # Coordinators must have first/last name and email
            if not cleaned_data.get("contact_first_name"):
                self.add_error("contact_first_name", "First name is required for coordinators.")
            if not cleaned_data.get("contact_last_name"):
                self.add_error("contact_last_name", "Last name is required for coordinators.")
            if not cleaned_data.get("email"):
                self.add_error("email", "Email is required for coordinators.")
        else:
            self.add_error("user_type", "User type is required.")

        return cleaned_data

    def clean_email(self):
        user_type = self.cleaned_data.get("user_type")
        email = self.cleaned_data.get("email")

        if user_type == "coordinator":
            if not email:
                raise ValidationError("Email is required for coordinators.")
            return email

        # Providers can have a blank email
        return email or ""

    def save(self, commit=True):
        user = super().save(commit=False)
        user_type = self.cleaned_data.get("user_type")

        if user_type == 'provider':
            agency_name = self.cleaned_data.get("agency_name", "").strip()
            user.display_name = agency_name
            user.email = f"{slugify(agency_name)}@provider.local"
        else:
            user.email = self.cleaned_data.get("email")
            first = self.cleaned_data.get('contact_first_name', '').strip()
            last = self.cleaned_data.get('contact_last_name', '').strip()
            user.display_name = f"{first} {last}".strip()

        if commit:
            user.save()
            from agency.models import UserProfile

            if user_type == 'provider':
                contact_first = ''
                contact_last = self.cleaned_data.get('agency_name', '')
            else:
                contact_first = self.cleaned_data.get('contact_first_name', '')
                contact_last = self.cleaned_data.get('contact_last_name', '')

            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'role': user_type,
                    'contact_first_name': contact_first,
                    'contact_last_name': contact_last,
                    'contact_email': self.cleaned_data.get('contact_email') or user.email,
                    'contact_phone_number': self.cleaned_data.get('contact_phone_number', ''),
                    'contact_address': self.cleaned_data.get('contact_address', ''),
                    'job_title': self.cleaned_data.get('job_title', ''),
                    'state': self.cleaned_data.get('state', ''),
                }
            )

            profile.role = user_type
            profile.agency_name = self.cleaned_data.get('agency_name', '')
            profile.counties.set(self.cleaned_data.get('counties'))
            profile.contact_first_name = contact_first
            profile.contact_last_name = contact_last

            #Save entity_type and image if available
            profile.entity_type = self.cleaned_data.get('entity_type', '')
            profile.profile_image = self.cleaned_data.get('profile_image', None)

            profile.save()

            print(f">>> Created profile for {user.email} (id={profile.id})")

        return user

class EmailAuthenticationForm(AuthenticationForm):
     username = forms.EmailField(
        label="Email",
         widget=forms.EmailInput(attrs={
            "autofocus": True,
            "class": "form-control",
            "placeholder": "Email"
        })
    )

class CustomLoginForm(forms.Form):
    user_type = forms.ChoiceField(
        choices=[('provider', 'Provider Agency'), ('coordinator', 'State/County Entity')],
        widget=forms.RadioSelect
    )
    agency_name = forms.CharField(required=False)
    username = forms.EmailField(required=False)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')

        if user_type == 'provider' and not cleaned_data.get('agency_name'):
            self.add_error('agency_name', 'Agency name is required for providers.')

        if user_type == 'coordinator' and not cleaned_data.get('username'):
            self.add_error('username', 'Email is required for coordinators.')

        return cleaned_data








