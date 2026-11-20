from .models import PageView

def log_page_view(request, page_name):
    """Utility to register user visits to various sections of the website."""
    user = request.user if request.user.is_authenticated else None
    PageView.objects.create(page_name=page_name, user=user)
