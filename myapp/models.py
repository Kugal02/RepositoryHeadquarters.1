from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

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
    ('community_living_services', 'Community Living Services'),
]


class Profile(models.Model):
    """
    Represents additional user-related information, such as agency name and phone number.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    agency_name = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.agency_name if self.agency_name else self.user.username


class Service(models.Model):
    """
    Represents a service with a key (code) and a readable name.
    """
    key = models.CharField(max_length=50, unique=True, choices=SERVICE_CHOICES)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class AgencyDetail(models.Model):
    """
    Stores detailed information about an agency, including services provided, referral limits,
    and whether the agency is currently accepting new referrals.
    """
    agency = models.ForeignKey(User, on_delete=models.CASCADE, related_name="agency_details")

    # Boolean fields for specific capabilities
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
    community_living_services = models.BooleanField(default=False)

    # Referral information
    accepting_referrals = models.BooleanField(default=False)
    referral_limit = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(10), MinValueValidator(0)]  # Added MinValueValidator
    )

    # Services provided as a ManyToMany relationship
    services_provided = models.ManyToManyField(Service, blank=True)

    # Timestamp of the last update
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.agency.profile.agency_name or self.agency.username} - Details"
