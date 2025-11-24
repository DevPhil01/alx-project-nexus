from django.http import JsonResponse

def home(request):
    """
    Simple homepage view for Render deployment.
    This helps avoid the 400 Bad Request error when opening the root URL.
    """
    return JsonResponse({
        "message": "Welcome to the Online Poll System API",
        "status": "running",
        "documentation": "/api/docs/",
        "polls_endpoint": "/api/polls/"
    })
