from django.shortcuts import redirect
from django.conf import settings
from django.utils import translation
from django.urls.base import resolve, reverse
from django.http import Http404, HttpResponseRedirect
from django.urls.exceptions import Resolver404
from urllib.parse import urlparse


def redirect_to_default_language(request):
    return redirect('/tk/')

def set_language(request, language):
    for lang, _ in settings.LANGUAGES:
        translation.activate(lang)
        try:
            view = resolve(urlparse(request.META.get("HTTP_REFERER")).path)
        except Resolver404:
            view = None
        if view:
            break
    if view:
        translation.activate(language)
        next_url = reverse(view.url_name, args=view.args, kwargs=view.kwargs)
        response = HttpResponseRedirect(next_url)
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)
    else:
        response = HttpResponseRedirect("/")
    return response