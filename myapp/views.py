import logging
import json
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import LoginForm, SignUpForm, AgencyDetailForm
from .models import Profile, AgencyDetail

# Set up logging
logger = logging.getLogger(__name__)

# Login View
def login_view(request):
    form = LoginForm(request, data=request.POST) if request.method == 'POST' else LoginForm()

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
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
    agencies = Profile.objects.all().order_by("agency_name")  # Fetch agencies in alphabetical order

    # Filter agencies based on accepting referrals status
    accepting_referrals = request.GET.get('accepting_referrals', '')
    if accepting_referrals:
        agencies = agencies.filter(agencydetail__accepting_referrals=(accepting_referrals.lower() == 'yes'))

    return render(request, 'myapp/dashboard.html', {'agencies': agencies})

# API: Get or Update Agency Details (AJAX Call)
@login_required
@login_required
def agency_details(request, agency_id):
    logger.info(f"Received request for agency ID: {agency_id}")

    try:
        # Ensure Profile exists
        agency = get_object_or_404(Profile, id=agency_id)

        # Ensure AgencyDetail exists for the agency
        agency_detail, created = AgencyDetail.objects.get_or_create(agency=agency.user)

        # Handle GET request (fetch agency details)
        if request.method == "GET":
            data = {
                "agency_name": agency.agency_name or "No Name Provided",
                "accepting_referrals": agency_detail.accepting_referrals,
                "last_updated": agency_detail.last_updated.strftime(
                    "%m/%d/%Y %I:%M %p") if agency_detail.last_updated else "Never Updated",
            }

            return JsonResponse(data)

        # Handle POST request (update accepting referrals)
        if request.method == "POST":
            try:
                data = json.loads(request.body)
                agency_detail.accepting_referrals = data.get("accepting_referrals", False)
                agency_detail.save()

                logger.info(f"Updated 'accepting_referrals' for agency {agency.agency_name} to {agency_detail.accepting_referrals}")

                return JsonResponse({"success": True})
            except Exception as e:
                logger.error(f"Error updating agency: {str(e)}")
                return JsonResponse({"error": "Failed to update agency details."}, status=500)

    except Exception as e:
        logger.error(f"Error fetching agency details for agency ID {agency_id}: {str(e)}")
        return JsonResponse({"error": f"Failed to fetch agency details: {str(e)}"}, status=500)


    except Exception as e:
        logger.error(f"Error fetching agency details for agency ID {agency_id}: {str(e)}")
        return JsonResponse({"error": "Failed to fetch agency details."}, status=500)

# Sign-Up View
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
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
