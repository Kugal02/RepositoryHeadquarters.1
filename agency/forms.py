from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from agency.models import UserProfile  # 👈 Correct placement

# Oregon counties
COUNTY_CHOICES = [
    ('baker', 'Baker'),
    ('benton', 'Benton'),
    ('clackamas', 'Clackamas'),
    ('clatsop', 'Clatsop'),
    ('columbia', 'Columbia'),
    ('coos', 'Coos'),
    ('crook', 'Crook'),
    ('curry', 'Curry'),
    ('deschutes', 'Deschutes'),
    ('douglas', 'Douglas'),
    ('gilliam', 'Gilliam'),
    ('grant', 'Grant'),
    ('harney', 'Harney'),
    ('hood_river', 'Hood River'),
    ('jackson', 'Jackson'),
    ('jefferson', 'Jefferson'),
    ('josephine', 'Josephine'),
    ('klamath', 'Klamath'),
    ('lake', 'Lake'),
    ('lane', 'Lane'),
    ('lincoln', 'Lincoln'),
    ('linn', 'Linn'),
    ('malheur', 'Malheur'),
    ('marion', 'Marion'),
    ('morrow', 'Morrow'),
    ('multnomah', 'Multnomah'),
    ('polk', 'Polk'),
    ('sherman', 'Sherman'),
    ('tillamook', 'Tillamook'),
    ('umatilla', 'Umatilla'),
    ('union', 'Union'),
    ('wallowa', 'Wallowa'),
    ('wasco', 'Wasco'),
    ('washington', 'Washington'),
    ('wheeler', 'Wheeler'),
    ('yamhill', 'Yamhill'),
]


class SignUpForm(forms.ModelForm):
    USER_TYPE_CHOICES = [
        ('provider', 'Provider Agency'),
        ('county', 'State/County Entity'),
    ]

    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, widget=forms.RadioSelect)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES)
    county = forms.CharField(max_length=100)

    agency_name = forms.CharField(max_length=100)
    contact_first_name = forms.CharField(max_length=50)
    contact_last_name = forms.CharField(max_length=50)
    agency_phone = forms.CharField(max_length=20)
    agency_email = forms.EmailField()
    counties = forms.MultipleChoiceField(
        choices=COUNTY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
    )
    state = forms.CharField(max_length=2, initial='OR')
    agree_to_terms = forms.BooleanField(label="I agree to the terms of service")

    class Meta:
        model = User
        fields = ['username', 'password', 'confirm_password', 'email']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")
        if password and confirm and password != confirm:
            raise ValidationError("Passwords do not match.")
