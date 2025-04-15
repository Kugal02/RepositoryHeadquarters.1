from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from .forms import CustomUserSignupForm, EmailAuthenticationForm
from agency.models import UserProfile
from django.urls import reverse
from django.contrib import messages


from django.urls import reverse

def signup_view(request):
    print(">>> USING ACCOUNTS.SIGNUP_VIEW <<<")

    if request.method == 'POST':
        print(">>> POST RECEIVED <<<")
        form = CustomUserSignupForm(request.POST)
        if form.is_valid():
            print(">>> FORM IS VALID <<<")
            user = form.save(commit=True)
            login(request, user)
            profile = user.userprofile
            user_type = form.cleaned_data.get("user_type")
            print(">>> PROFILE ID:", profile.id)
            print(">>> USER TYPE:", user_type)

            if user_type == 'provider':
                return redirect(f"{reverse('dashboard')}?provider_id={profile.id}")
            else:
                # Redirect coordinators to their edit page
                return redirect('edit_coordinator_profile')

        else:
            messages.error(request, "There was an error with your form submission. Please fix the errors below.")
    else:
        form = CustomUserSignupForm()

    return render(request, 'registration/signup.html', {'form': form})


class CustomLoginView(LoginView):
    authentication_form = EmailAuthenticationForm
    template_name = 'registration/login.html'  # make sure this matches your actual template

