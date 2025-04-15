from django.conf import settings
from django.db import models
from django.core.validators import MaxValueValidator


class County(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('provider', 'Provider Agency'),
        ('coordinator', 'State/County Entity'),
    ]

    ENTITY_TYPE_CHOICES = [
        ('odds', 'ODDS'),
        ('vr', 'VR'),
    ]

    entity_type = models.CharField(
        max_length=10,
        choices=ENTITY_TYPE_CHOICES,
        blank=True,
        null=True,
        help_text="Applicable only to State/County Entities"
    )

    state = models.CharField(
        max_length=2,
        choices=[
            ('OR', 'Oregon'),
        ],

        blank=True,
        null=True
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="userprofile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    agency_name = models.CharField(max_length=255, null=True, blank=True, help_text="Used by provider agencies to store their official name")

    counties = models.ManyToManyField(County, blank=True)

    contact_first_name = models.CharField(max_length=50, null=True, blank=True)
    contact_last_name = models.CharField(max_length=50, default='')
    contact_phone_number = models.CharField(max_length=20, null=True, blank=True)
    contact_email = models.EmailField(null=True, blank=True)
    contact_address = models.CharField(max_length=500, null=True, blank=True)
    job_title = models.CharField(max_length=50, null=True, blank=True)

    referral_status = models.CharField(
        max_length=20,
        choices=[('accepting', 'Accepting Referrals'), ('not_accepting', 'Not Accepting Referrals')],
        default='not_accepting'
    )

    # Service booleans
    residential_referrals = models.BooleanField(default=False)
    afc_referrals = models.BooleanField(default=False)
    behavior_referrals = models.BooleanField(default=False)
    dsa_facility_referrals = models.BooleanField(default=False)
    dsa_community_referrals = models.BooleanField(default=False)
    dsa_community_solo_referrals = models.BooleanField(default=False)
    vocational_rehabilitation_referrals = models.BooleanField(default=False)
    career_exploration_referrals = models.BooleanField(default=False)
    job_development_referrals = models.BooleanField(default=False)
    job_coaching_referrals = models.BooleanField(default=False)
    job_search_assistance_referrals = models.BooleanField(default=False)
    employment_path_community_referrals = models.BooleanField(default=False)
    employment_path_community_solo_referrals = models.BooleanField(default=False)
    adl_iadl_referrals = models.BooleanField(default=False)

    # Editable counts
    residential_referrals_count = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(99)])
    afc_referrals_count = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(99)])
    behavior_referrals_count = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(99)])
    dsa_facility_referrals_count = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(99)])
    dsa_community_referrals_count = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(99)])
    dsa_community_solo_referrals_count = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(99)])
    vocational_rehabilitation_referrals_count = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(99)])
    career_exploration_referrals_count = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(99)])
    job_development_referrals_count = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(99)])
    job_coaching_referrals_count = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(99)])
    job_search_assistance_referrals_count = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(99)])
    employment_path_community_referrals_count = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(99)])
    employment_path_community_solo_referrals_count = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(99)])
    adl_iadl_referrals_count = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(99)])

    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    notes = models.TextField(max_length=500, blank=True, null=True)
    website = models.URLField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.user.email} ({self.role})"


class Contact(models.Model):
    user_profile = models.ForeignKey(UserProfile, related_name='contacts', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    address = models.CharField(max_length=500, null=True, blank=True)
    contact_type = models.CharField(max_length=50, null=True, blank=True)
    other_service_desc = models.CharField(max_length=100, null=True, blank=True)

class CommunityPost(models.Model):
    POST_TYPE_CHOICES = [
        ('event', 'Event'),
        ('placement', 'Job Placement'),
        ('employer', 'Employer Hiring'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    post_type = models.CharField(max_length=20, choices=POST_TYPE_CHOICES)
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Optional fields for event/employer
    event_date = models.DateField(null=True, blank=True)
    employer_name = models.CharField(max_length=255, blank=True)
    employer_website = models.URLField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.post_type})"

    # models.py

class PostReaction(models.Model):
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name='reactions')
    emoji = models.CharField(max_length=10)  # E.g., "🎉"
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'emoji', 'user')  # One emoji per user per post

    def __str__(self):
        return f"{self.user} reacted {self.emoji} to {self.post.title}"
