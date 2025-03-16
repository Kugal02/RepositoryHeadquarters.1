from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator

# Define service choices globally, outside of any class
SERVICE_CHOICES = [
    ('job_development', 'Job Development'),
    ('employment_path_community', 'Employment Path-Community'),
    ('employment_path_solo', 'Employment Path Solo'),
    ('job_coaching_vr', 'Job Coaching (VR)'),
    ('job_coaching_odds', 'Job Coaching (ODDS)'),
    ('career_exploration', 'Career Exploration'),
    ('targeted_vocational_assessments', 'Targeted Vocational Assessments'),
    ('community_based_work_assessments', 'Community Based Work Assessments'),
    ('job_retention', 'Job Retention'),
    ('discovery', 'Discovery'),
    ('dsa_facility', 'DSA (Facility)'),
    ('dsa_community', 'DSA (Community)'),
    ('adl_iadl', 'ADL/IADL'),
]

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    agency_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.agency_name if self.agency_name else self.user.username


class AgencyDetail(models.Model):
    agency = models.OneToOneField(User, on_delete=models.CASCADE, related_name="agency_detail")

    # Boolean fields for each service
    job_development = models.BooleanField(default=False)
    employment_path_community = models.BooleanField(default=False)
    employment_path_solo = models.BooleanField(default=False)
    job_coaching_vr = models.BooleanField(default=False)
    job_coaching_odds = models.BooleanField(default=False)
    career_exploration = models.BooleanField(default=False)
    targeted_vocational_assessments = models.BooleanField(default=False)
    community_based_work_assessments = models.BooleanField(default=False)
    job_retention = models.BooleanField(default=False)
    discovery = models.BooleanField(default=False)
    dsa_facility = models.BooleanField(default=False)
    dsa_community = models.BooleanField(default=False)
    adl_iadl = models.BooleanField(default=False)

    # Accepting referrals (Yes/No field)
    accepting_referrals = models.BooleanField(default=False)

    # New number field to track the number of referrals accepted (max 10)
    referral_limit = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(10)]  # Restrict referral limit to a max of 10
    )

    # Referral services list
    referral_services = models.JSONField(default=list)  # Store list of selected referral services

    last_updated = models.DateTimeField(auto_now=True)  # Auto-updates whenever the form is saved

    def __str__(self):
        return f"{self.agency.username} - Details"
