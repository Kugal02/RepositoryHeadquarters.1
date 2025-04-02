from django.contrib.auth import login
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.http import JsonResponse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.timezone import localtime, now
from datetime import datetime, timedelta, timezone
from io import BytesIO
from reportlab.pdfgen import canvas
from .forms import SignUpForm
from .forms import UserProfileEditForm
import csv
import json
from .models import County, UserProfile


@login_required
def edit_user_profile(request):
    user_profile = request.user.userprofile
    if request.method == 'POST':
        form = UserProfileEditForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect(f'/dashboard/?provider_id={user_profile.id}')
    else:
        form = UserProfileEditForm(instance=user_profile)
    return render(request, 'agency/edit_profile.html', {'form': form})


def update_referral(request):
    if request.method == 'POST':
        # Decode the JSON data from the request body
        data = json.loads(request.body)
        referral_type = data.get('referral_type')
        new_value = data.get('new_value')

        # Make sure the new value is a valid number
        try:
            new_value = int(new_value)
        except ValueError:
            return JsonResponse({"error": "Invalid value."}, status=400)

        # Get the user's profile and update the appropriate referral field
        user_profile = request.user.userprofile

        if hasattr(user_profile, referral_type):  # Check if the field exists on the UserProfile
            setattr(user_profile, referral_type, new_value)  # Set the new value
            user_profile.save()  # Save the changes

            return JsonResponse({"success": "Referral updated successfully."})
        else:
            return JsonResponse({"error": "Invalid referral field."}, status=400)
    else:
        return JsonResponse({"error": "Invalid request method."}, status=405)


def update_referral_status(request):
    if request.method == 'POST':
        # Get new referral status from the request body
        referral_status = request.POST.get('referral_status')
        user_profile = request.user.userprofile

        # Update the referral status
        user_profile.referral_status = referral_status

        if referral_status == 'not_accepting':
            # Set all referral counts to 0 when not accepting
            user_profile.residential_referrals = 0
            user_profile.afc_referrals = 0
            user_profile.behavior_referrals = 0
            user_profile.dsa_facility_referrals = 0
            user_profile.dsa_community_referrals = 0
            user_profile.dsa_community_solo_referrals = 0
            user_profile.vocational_rehabilitation_referrals = 0
            user_profile.career_exploration_referrals = 0
            user_profile.job_development_referrals = 0
            user_profile.job_coaching_referrals = 0
            user_profile.job_search_assistance_referrals = 0
            user_profile.employment_path_community_referrals = 0
            user_profile.employment_path_community_solo_referrals = 0
            user_profile.adl_iadl_referrals = 0

        # Save the changes
        user_profile.save()

        return JsonResponse({"success": True, "referral_status": referral_status})
    return JsonResponse({"error": "Invalid request method"}, status=400)


class CustomPasswordResetView(PasswordResetView):
    email_template_name = 'registration/password_reset_email.txt'
    html_email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'

    def form_valid(self, form):
        user = form.get_users().__next__()
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        opts = {
            'use_https': self.request.is_secure(),
            'token_generator': self.token_generator,
            'from_email': self.from_email,
            'email_template_name': self.email_template_name,
            'subject_template_name': self.subject_template_name,
            'request': self.request,
            'html_email_template_name': self.html_email_template_name,
            'extra_email_context': {
                'uid': uid,
                'token': token,
                'reset_url': f"{self.request.scheme}://{self.request.get_host()}/reset/{uid}/{token}/"
            }
        }

        return form.save(**opts)


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            # Check if the username already exists
            username = form.cleaned_data['username']
            if User.objects.filter(username=username).exists():
                messages.error(request, "This username is already taken. Please choose a different username.")
                return render(request, 'signup.html', {'form': form})

            # Create the User
            user = User.objects.create_user(
                username=username,
                password=form.cleaned_data['password']  # This will automatically hash the password
            )

            # Check if the UserProfile already exists for this user
            user_profile, created = UserProfile.objects.get_or_create(user=user)  # get_or_create will avoid duplicates

            if created:
                user_profile.state = form.cleaned_data['state']
                user_profile.counties.set(form.cleaned_data['counties'])
                user_profile.save()

            # Login the user after successful signup
            login(request, user)

            # Redirect to the dashboard or another page
            return redirect('dashboard')
        else:
            print(form.errors)  # Debugging: Output form errors to console
    else:
        form = SignUpForm()

    counties = County.objects.all()
    return render(request, 'signup.html', {'form': form})


@login_required
def dashboard(request):
    user_profile = request.user.userprofile
    referral_status_filter = request.GET.get('referral_status', '')
    all_providers = UserProfile.objects.filter(role='provider').order_by('user__username')
    print("Number of Providers:", all_providers.count())

    if referral_status_filter:
        all_providers = all_providers.filter(referral_status=referral_status_filter)

    if user_profile.referral_status == 'not_accepting':
        user_profile.residential_referrals = 0
        user_profile.afc_referrals = 0
        user_profile.behavior_referrals = 0
        user_profile.dsa_facility_referrals = 0
        user_profile.dsa_community_referrals = 0
        user_profile.dsa_community_solo_referrals = 0
        user_profile.vocational_rehabilitation_referrals = 0
        user_profile.career_exploration_referrals = 0
        user_profile.vocational_assessments_referrals = 0
        user_profile.job_development_referrals = 0
        user_profile.job_coaching_referrals = 0
        user_profile.job_search_assistance_referrals = 0
        user_profile.employment_path_community_referrals = 0
        user_profile.employment_path_community_solo_referrals = 0
        user_profile.adl_iadl_referrals = 0
        user_profile.save()

    selected_provider = None
    last_login_display = None
    last_login_status = None

    if request.GET.get('provider_id'):
        try:
            selected_provider = UserProfile.objects.get(id=request.GET['provider_id'])

            # 🔍 Check and format last login
            last_login = selected_provider.user.last_login
            if last_login:
                pacific_login_time = localtime(last_login)  # Localize to Pacific Time
                last_login_display = pacific_login_time.strftime("%m/%d/%Y %I:%M%p").lower()

                # Use localtime for both values to compare correctly
                days_since = (localtime(now()) - pacific_login_time).days
                last_login_status = "old" if days_since >= 4 else "recent"
        except UserProfile.DoesNotExist:
            messages.error(request, "The selected provider does not exist.")
            selected_provider = None

    distinct_counties = County.objects.filter(userprofile__role='provider').distinct()

    return render(request, 'dashboard.html', {
        'profile': user_profile,
        'all_providers': all_providers,
        'selected_provider': selected_provider,
        'distinct_counties': distinct_counties,
        'accepting': user_profile.referral_status == 'accepting',
        'referral_status_filter': referral_status_filter,
        'last_login_display': last_login_display,
        'last_login_status': last_login_status,
    })


@login_required
def state_county_entities(request):
    search_query = request.GET.get('q', '').strip()
    providers = UserProfile.objects.filter(role='coordinator')

    if search_query:
        providers = providers.filter(
            Q(agency_name__icontains=search_query) |
            Q(county__icontains=search_query)
        )

    providers = providers.order_by('county', 'agency_name')

    paginator = Paginator(providers, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    distinct_counties = County.objects.filter(userprofile__role='owner').distinct()

    return render(request, 'state_county_entities.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'distinct_counties': distinct_counties,
    })


def export_csv(request):
    providers = UserProfile.objects.filter(role='owner').order_by('county', 'agency_name')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="state_county_entities.csv"'

    writer = csv.writer(response)
    writer.writerow(['County', 'Agency Name', 'Phone', 'Email'])

    for provider in providers:
        writer.writerow([provider.county, provider.agency_name, provider.agency_phone, provider.agency_email])

    return response


def export_pdf(request):
    providers = UserProfile.objects.filter(role='owner').order_by('county', 'agency_name')

    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    y = 800

    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, y, "State/County Entities")
    y -= 30

    p.setFont("Helvetica", 10)
    for provider in providers:
        line = f"{provider.county} - {provider.agency_name}, {provider.agency_phone}, {provider.agency_email}"
        p.drawString(40, y, line)
        y -= 15
        if y < 50:
            p.showPage()
            y = 800

    p.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="state_county_entities.pdf"'
    return response


def home_redirect(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        return redirect('login')
