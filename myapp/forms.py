from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile, AgencyDetail, SERVICE_CHOICES  # Import SERVICE_CHOICES here

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
    services_provided = forms.MultipleChoiceField(
        choices=SERVICE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    accepting_referrals = forms.BooleanField(required=False)
    referral_limit = forms.IntegerField(
        required=False,
        min_value=0,
        max_value=10,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max referrals (1-10)'})
    )
    referral_services = forms.MultipleChoiceField(
        choices=SERVICE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = AgencyDetail
        fields = ['services_provided', 'accepting_referrals', 'referral_limit', 'referral_services']  # List the fields you want to display
