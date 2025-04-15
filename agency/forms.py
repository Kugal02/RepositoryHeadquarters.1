from django import forms
from .models import County, UserProfile, CommunityPost
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class SignUpForm(UserCreationForm):
    USER_TYPE_CHOICES = [
        ('provider', 'Provider Agency'),
        ('coordinator', 'State/County Entity'),
    ]

    role = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        widget=forms.RadioSelect,
        required=True,
        label="User Type"
    )

    STATE_CHOICES = [
        ('OR', 'Oregon'),
    ]

    state = forms.ChoiceField(
        choices=sorted(STATE_CHOICES, key=lambda x: x[1]),
        widget=forms.Select,
        initial='OR',
        required=True,
        label='State'
    )

    counties = forms.ModelMultipleChoiceField(
        queryset=County.objects.none(),
        widget=forms.CheckboxSelectMultiple
    )

    agree_to_terms = forms.BooleanField(
        label="I agree to the Terms of Service",
        required=True
    )

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['counties'].queryset = County.objects.all()
        self.fields['state'].widget = forms.Select()


class UserProfileEditForm(forms.ModelForm):
    profile_image = forms.ImageField(required=False)

    # Service toggles
    residential_referrals = forms.BooleanField(required=False)
    afc_referrals = forms.BooleanField(required=False)
    behavior_referrals = forms.BooleanField(required=False)
    dsa_facility_referrals = forms.BooleanField(required=False)
    dsa_community_referrals = forms.BooleanField(required=False)
    dsa_community_solo_referrals = forms.BooleanField(required=False)
    vocational_rehabilitation_referrals = forms.BooleanField(required=False)
    career_exploration_referrals = forms.BooleanField(required=False)
    job_development_referrals = forms.BooleanField(required=False)
    job_coaching_referrals = forms.BooleanField(required=False)
    job_search_assistance_referrals = forms.BooleanField(required=False)
    employment_path_community_referrals = forms.BooleanField(required=False)
    employment_path_community_solo_referrals = forms.BooleanField(required=False)
    adl_iadl_referrals = forms.BooleanField(required=False)

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
            'agency_name',
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


class CommunityPostForm(forms.ModelForm):
    class Meta:
        model = CommunityPost
        fields = [
            'county',
            'post_type',
            'event_date',
            'title',
            'description',
            'employer_name',
            'employer_website',
        ]
        widgets = {
            'county': forms.Select(attrs={'class': 'form-control'}),
            'post_type': forms.Select(attrs={'class': 'form-control'}),
            'event_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'maxlength': '750',
                'rows': 4,
                'placeholder': 'Enter a brief description (max 750 characters)'
            }),
            'employer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'employer_website': forms.URLInput(attrs={'class': 'form-control'}),
        }

class CoordinatorProfileEditForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'entity_type',
            'state',
            'counties',
            'contact_first_name',
            'contact_last_name',
            'contact_email',
            'contact_phone_number',
            'contact_address',
            'job_title',
            'profile_image',
            'notes',
            'website',
        ]
        widgets = {
            'counties': forms.CheckboxSelectMultiple(),
            'notes': forms.Textarea(attrs={'rows': 3, 'maxlength': '500'}),
        }

