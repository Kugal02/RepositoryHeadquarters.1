from django import forms
from .models import County, UserProfile
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class SignUpForm(forms.ModelForm):
    USER_TYPE_CHOICES = [
        ('provider', 'Provider Agency'),
        ('coordinator', 'State/County Entity'),
    ]

    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        widget=forms.RadioSelect,
        required=True
    )

    username = forms.CharField(max_length=75, label="Agency Name")
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    STATE_CHOICES = [
        ('OR', 'Oregon'),
        ('WA', 'Washington'),
        ('CA', 'California'),
    ]
    state = forms.ChoiceField(choices=sorted(STATE_CHOICES, key=lambda x: x[1]), initial='OR', required=True)

    counties = forms.ModelMultipleChoiceField(
        queryset=County.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )

    agree_to_terms = forms.BooleanField(
        label="I agree to the Terms of Service",
        required=True
    )

    class Meta:
        model = User
        fields = ['user_type', 'username', 'password', 'confirm_password', 'state', 'counties', 'agree_to_terms']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")
        if password and confirm and password != confirm:
            raise ValidationError("Passwords do not match.")

class UserProfileEditForm(forms.ModelForm):
    profile_image = forms.ImageField(required=False)

    # Service toggles
    residential_referrals = forms.BooleanField(required=False, label="Accepting Residential Services")
    afc_referrals = forms.BooleanField(required=False, label="Accepting Adult Foster Care")
    behavior_referrals = forms.BooleanField(required=False, label="Accepting Behavior Services")
    dsa_facility_referrals = forms.BooleanField(required=False, label="Accepting DSA Facility Services")
    dsa_community_referrals = forms.BooleanField(required=False, label="Accepting DSA Community Services")
    dsa_community_solo_referrals = forms.BooleanField(required=False, label="Accepting DSA Community Solo Services")
    vocational_rehabilitation_referrals = forms.BooleanField(required=False, label="Accepting Vocational Rehabilitation Services")
    career_exploration_referrals = forms.BooleanField(required=False, label="Accepting Career Exploration Services")
    job_development_referrals = forms.BooleanField(required=False, label="Accepting Job Development Services")
    job_coaching_referrals = forms.BooleanField(required=False, label="Accepting Job Coaching Services")
    job_search_assistance_referrals = forms.BooleanField(required=False, label="Accepting Job Search Assistance Services")
    employment_path_community_referrals = forms.BooleanField(required=False, label="Accepting Employment Path Community Services")
    employment_path_community_solo_referrals = forms.BooleanField(required=False, label="Accepting Employment Path Community Solo Services")
    adl_iadl_referrals = forms.BooleanField(required=False, label="Accepting ADL/IADL Services")

    # Count inputs
    residential_referrals_count = forms.IntegerField(required=False, min_value=0, max_value=99)
    afc_referrals_count = forms.IntegerField(required=False, min_value=0, max_value=99)
    behavior_referrals_count = forms.IntegerField(required=False, min_value=0, max_value=99)
    dsa_facility_referrals_count = forms.IntegerField(required=False, min_value=0, max_value=99)
    dsa_community_referrals_count = forms.IntegerField(required=False, min_value=0, max_value=99)
    dsa_community_solo_referrals_count = forms.IntegerField(required=False, min_value=0, max_value=99)
    vocational_rehabilitation_referrals_count = forms.IntegerField(required=False, min_value=0, max_value=99)
    career_exploration_referrals_count = forms.IntegerField(required=False, min_value=0, max_value=99)
    job_development_referrals_count = forms.IntegerField(required=False, min_value=0, max_value=99)
    job_coaching_referrals_count = forms.IntegerField(required=False, min_value=0, max_value=99)
    job_search_assistance_referrals_count = forms.IntegerField(required=False, min_value=0, max_value=99)
    employment_path_community_referrals_count = forms.IntegerField(required=False, min_value=0, max_value=99)
    employment_path_community_solo_referrals_count = forms.IntegerField(required=False, min_value=0, max_value=99)
    adl_iadl_referrals_count = forms.IntegerField(required=False, min_value=0, max_value=99)


    class Meta:
        model = UserProfile
        fields = [
            'contact_first_name', 'contact_last_name', 'contact_address',
            'contact_phone_number', 'contact_email', 'referral_status',
            'residential_referrals', 'afc_referrals', 'behavior_referrals',
            'dsa_facility_referrals', 'dsa_community_referrals', 'dsa_community_solo_referrals',
            'vocational_rehabilitation_referrals', 'career_exploration_referrals',
            'job_development_referrals', 'job_coaching_referrals', 'job_search_assistance_referrals',
            'employment_path_community_referrals', 'employment_path_community_solo_referrals',
            'adl_iadl_referrals',
            'residential_referrals_count', 'afc_referrals_count', 'behavior_referrals_count',
            'dsa_facility_referrals_count', 'dsa_community_referrals_count', 'dsa_community_solo_referrals_count',
            'vocational_rehabilitation_referrals_count', 'career_exploration_referrals_count',
            'job_development_referrals_count', 'job_coaching_referrals_count',
            'job_search_assistance_referrals_count', 'employment_path_community_referrals_count',
            'employment_path_community_solo_referrals_count', 'adl_iadl_referrals_count',
            'profile_image',
            'notes',
            'website',
        ]
        widgets = {
            'notes': forms.Textarea(attrs={
                'maxlength': '300',
                'rows': 4,
                'placeholder': 'Add notes here (max 300 characters)',
                'class': 'form-control',
            }),
        }

    def clean(self):
        cleaned_data = super().clean()

        for field_name in self.fields:
            if field_name.endswith('_referrals') and not field_name.endswith('_referrals_count'):
                count_field = f"{field_name}_count"
                is_checked = cleaned_data.get(field_name)
                count_value = cleaned_data.get(count_field)

                if is_checked and (count_value is None):
                    self.add_error(count_field, "This field is required when the service is selected.")

        return cleaned_data

    class SignUpForm(forms.Form):  # or forms.ModelForm
        # other fields ...
        counties = forms.ModelMultipleChoiceField(
            queryset=County.objects.all(),
            widget=forms.CheckboxSelectMultiple,
            required=True
        )
