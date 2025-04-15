import requests
from django.conf import settings

def send_mailgun_email(subject, message, recipient):
    """
    Function to send email using Mailgun API.
    """
    api_url = f"https://api.mailgun.net/v3/{settings.MAILGUN_DOMAIN}/messages"
    auth = ("api", settings.MAILGUN_API_KEY)  # Basic auth with API key

    # Data payload for Mailgun API request
    data = {
        "from": f"noreply@{settings.MAILGUN_DOMAIN}",
        "to": recipient,
        "subject": subject,
        "text": message,
    }

    # Make the HTTP POST request to Mailgun API
    response = requests.post(api_url, auth=auth, data=data)

    # Check if the request was successful
    if response.status_code == 200:
        return True
    else:
        return False
