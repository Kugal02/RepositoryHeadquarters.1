from django.contrib import admin
from .models import UserProfile, County, Contact, CommunityPost


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'job_title', 'entity_type', 'referral_status')
    list_display_links = ('user',)  # Make usernames clickable
    search_fields = ('user__username', 'contact_first_name', 'contact_last_name', 'job_title')
    list_filter = ('role', 'referral_status', 'entity_type', 'counties')

    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'role', 'entity_type', 'counties')
        }),
        ('Contact Details', {
            'fields': (
                'contact_first_name', 'contact_last_name',
                'contact_phone_number', 'contact_email',
                'contact_address', 'job_title'
            )
        }),
        ('Referral Settings', {
            'fields': (
                'referral_status',
                'residential_referrals', 'afc_referrals', 'behavior_referrals',
                'dsa_facility_referrals', 'dsa_community_referrals', 'dsa_community_solo_referrals',
                'vocational_rehabilitation_referrals', 'career_exploration_referrals',
                'job_development_referrals', 'job_coaching_referrals', 'job_search_assistance_referrals',
                'employment_path_community_referrals', 'employment_path_community_solo_referrals',
                'adl_iadl_referrals'
            )
        }),
        ('Referral Counts', {
            'fields': (
                'residential_referrals_count', 'afc_referrals_count', 'behavior_referrals_count',
                'dsa_facility_referrals_count', 'dsa_community_referrals_count', 'dsa_community_solo_referrals_count',
                'vocational_rehabilitation_referrals_count', 'career_exploration_referrals_count',
                'job_development_referrals_count', 'job_coaching_referrals_count', 'job_search_assistance_referrals_count',
                'employment_path_community_referrals_count', 'employment_path_community_solo_referrals_count',
                'adl_iadl_referrals_count'
            )
        }),
        ('Other', {
            'fields': ('profile_image', 'notes', 'website')
        }),
    )


@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    search_fields = ['name']
    verbose_name_plural = "Counties"  # 👈 this fixes the plural spelling

@admin.register(Contact)  # Register the Contact model
class ContactAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number', 'user_profile')  # Fields to display in the list
    search_fields = ('first_name', 'last_name', 'email')  # Fields to search by in the admin
    list_filter = ('contact_type',)  # You can filter by contact type (optional)
    raw_id_fields = ('user_profile',)  # This links the contact to the user profile via the user_profile ID

# Register CommunityPost model
@admin.register(CommunityPost)
class CommunityPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'post_type', 'county', 'created_by', 'created_at')
    list_filter = ('post_type', 'county', 'created_at')
    search_fields = ('title', 'description', 'employer_name')
