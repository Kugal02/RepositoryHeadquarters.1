from django.http import HttpResponse

def dashboard(request):
    return HttpResponse("<h1>Provider Agency Dashboard</h1>")
