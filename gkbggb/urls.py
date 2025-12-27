"""
URL configuration for gkbggb project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.i18n import i18n_patterns
from .views import redirect_to_default_language, set_language
from django.urls import re_path
from django.conf.urls.static import static
from django.conf import settings
from django.views.static import serve
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('nested_admin/', include('nested_admin.urls')),
    path('admin/', admin.site.urls),
    path('login/', LoginView.as_view(), name='login'),
    path('accounts/', include('django.contrib.auth.urls')), 
    path('set_language/<str:language>/', set_language, name='set-language'),
    path('', include('report.urls')),
]

# Wrapping the base urlpatterns with i18n patterns
# urlpatterns = i18n_patterns(*urlpatterns, prefix_default_language=False)

urlpatterns = [
    *i18n_patterns(*urlpatterns, prefix_default_language=True),
    path("set_language/<str:language>", set_language, name="set-language"),
        re_path(r'^media/(?P<path>.*)$', serve,
            {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve,
            {'document_root': settings.STATIC_ROOT}),
]

# Static and media file serving during development
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]

# Ensure correct static and media URL handling for development or deployment
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Add i18n URLs
urlpatterns += [path('i18n/', include('django.conf.urls.i18n')),]
    

admin.site.site_header = 'Report Management'
admin.site.site_title = "Report Management"
admin.site.index_title = "Report Management"