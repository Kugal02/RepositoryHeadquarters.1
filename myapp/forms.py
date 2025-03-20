from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile, AgencyDetail, SERVICE_CHOICES


# Login Form (for user authentication)
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'})
    )


# Sign-Up Form (for user registration)
class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
    )
    phone_number = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'})
    )
    agency_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your agency name'})
    )

    class Meta:
        model = User  # This is the built-in Django User model
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)  # Save User but don't commit yet
        if commit:
            user.save()
            Profile.objects.create(  # Create a Profile linked to the user
                user=user,
                phone_number=self.cleaned_data['phone_number'],
                agency_name=self.cleaned_data['agency_name']
            )
        return user


class AgencyDetailForm(forms.ModelForm):
    # Checkboxes for services (listed from SERVICE_CHOICES)
    job_development = forms.BooleanField(required=False, label="Job Development")
    employment_path_community = forms.BooleanField(required=False, label="Employment Path - Community")
    employment_path_solo = forms.BooleanField(required=False, label="Employment Path - Solo")
    job_coaching_vr = forms.BooleanField(required=False, label="Job Coaching (VR)")
    job_coaching_odds = forms.BooleanField(required=False, label="Job Coaching (ODDS)")
    career_exploration = forms.BooleanField(required=False, label="Career Exploration")
    targeted_vocational_assessments = forms.BooleanField(required=False, label="Targeted Vocational Assessments")
    community_based_work_assessments = forms.BooleanField(required=False, label="Community-Based Work Assessments")
    job_retention = forms.BooleanField(required=False, label="Job Retention")
    discovery = forms.BooleanField(required=False, label="Discovery")
    dsa_facility = forms.BooleanField(required=False, label="DSA (Facility)")
    dsa_community = forms.BooleanField(required=False, label="DSA (Community)")
    adl_iadl = forms.BooleanField(required=False, label="ADL/IADL")
    community_living_services = forms.BooleanField(required=False, label="Community Living Services")

    accepting_referrals = forms.BooleanField(required=False, label="Accepting Referrals")
    referral_limit = forms.IntegerField(
        required=False,
        min_value=0,
        max_value=10,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max referrals (1-10)'}),
        label="Referral Limit"
    )

    class Meta:
        model = AgencyDetail
        fields = [
            # Include all fields for services as part of the form
            'job_development',
            'employment_path_community',
            'employment_path_solo',
            'job_coaching_vr',
            'job_coaching_odds',
            'career_exploration',
            'targeted_vocational_assessments',
            'community_based_work_assessments',
            'job_retention',
            'discovery',
            'dsa_facility',
            'dsa_community',
            'adl_iadl',
            'community_living_services',
            'accepting_referrals',
            'referral_limit',
        ]

    def clean(self):
        cleaned_data = super().clean()
        accepting_referrals = cleaned_data.get("accepting_referrals")

        # If not accepting referrals, automatically uncheck all services
        if not accepting_referrals:
            for field in self.Meta.fields:
                if field not in ['accepting_referrals', 'referral_limit']:
                    cleaned_data[field] = False

        return cleaned_data
