from .models import ThemeSettings

def theme_settings(request):
    """
    Nạp cấu hình giao diện vào toàn cục template.
    """
    settings_obj = ThemeSettings.load()
    return {
        'theme': settings_obj
    }
