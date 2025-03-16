from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import LoginForm, SignUpForm, AgencyDetailForm
from .models import Profile, AgencyDetail

# Login View
def login_view(request):
    form = LoginForm(request, data=request.POST) if request.method == 'POST' else LoginForm()

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Login successful! Welcome back.")
            return redirect('dashboard')  # Redirect to dashboard
        else:
            messages.error(request, "Invalid username or password. Please try again.")

    return render(request, 'myapp/login.html', {'form': form})

# Logout View
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')

# Dashboard View (Protected - Requires Login)
@login_required
def dashboard_view(request):
    agencies = Profile.objects.all().order_by("agency_name")  # Fetch agencies
    return render(request, 'myapp/dashboard.html', {'agencies': agencies})

# API: Get or Update Agency Details (AJAX Call)
@login_required
def agency_details(request, agency_id):
    # Fetch the agency profile
    agency = get_object_or_404(Profile, id=agency_id)
    # Get or create agency details
    agency_detail, created = AgencyDetail.objects.get_or_create(agency=agency.user)

    is_owner = request.user == agency.user  # Check if the logged-in user is the owner

    if request.method == 'POST':
        if not is_owner:  # Prevent non-owners from editing
            return JsonResponse({"error": "You do not have permission to edit this agency."}, status=403)

        form = AgencyDetailForm(request.POST, instance=agency_detail)
        if form.is_valid():
            form.save()
            return JsonResponse({"message": "Agency details updated successfully!"})
        else:
            return JsonResponse({"errors": form.errors}, status=400)

    # Prepare the data to send back to the frontend
    data = {
        "agency_name": agency.agency_name,
        "accepting_referrals": agency_detail.accepting_referrals,
        "referral_services": agency_detail.referral_services if agency_detail else [],
        "last_updated": agency_detail.last_updated.strftime("%Y-%m-%d %H:%M:%S") if agency_detail else "Never Updated",
        "is_owner": is_owner,  # Send permission flag to frontend

        # Replace services_provided with individual boolean fields
        "services_provided": [
            "Job Development" if agency_detail.job_development else None,
            "Employment Path-Community" if agency_detail.employment_path_community else None,
            "Employment Path Solo" if agency_detail.employment_path_solo else None,
            "Job Coaching (VR)" if agency_detail.job_coaching_vr else None,
            "Job Coaching (ODDS)" if agency_detail.job_coaching_odds else None,
            "Career Exploration" if agency_detail.career_exploration else None,
            "Targeted Vocational Assessments" if agency_detail.targeted_vocational_assessments else None,
            "Community Based Work Assessments" if agency_detail.community_based_work_assessments else None,
            "Job Retention" if agency_detail.job_retention else None,
            "Discovery" if agency_detail.discovery else None,
            "DSA (Facility)" if agency_detail.dsa_facility else None,
            "DSA (Community)" if agency_detail.dsa_community else None,
            "ADL/IADL" if agency_detail.adl_iadl else None
        ]
    }

    # Remove None values from the services_provided list (if there are no services)
    data["services_provided"] = [service for service in data["services_provided"] if service]

    # If there are no services, ensure services_provided is still an empty list
    if not data["services_provided"]:
        data["services_provided"] = []

    # Ensure referral_count is included if accepting referrals
    if agency_detail.accepting_referrals:
        data["referral_count"] = agency_detail.referral_limit  # Add referral limit count

    return JsonResponse(data)


# Sign-Up View (Fix Profile Saving)
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()  # Save user first
                Profile.objects.update_or_create(
                    user=user,
                    defaults={
                        "phone_number": form.cleaned_data.get("phone_number"),
                        "agency_name": form.cleaned_data.get("agency_name"),
                    }
                )
                login(request, user)
                messages.success(request, "Account created successfully! You are now logged in.")
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f"An unexpected error occurred: {e}")

        else:
            messages.error(request, "Please correct the errors below.")

    else:
        form = SignUpForm()

    return render(request, 'myapp/signup.html', {'form': form})

# Terms of Service View
def terms(request):
    return render(request, 'myapp/terms.html')
