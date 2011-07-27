from django.http import HttpResponse
import os
import cgi
import datetime
import urllib
import wsgiref.handlers

from django.http import HttpResponseRedirect
from django.template import Context, Template
from django.template.loader import get_template

from google.appengine.ext import db
from google.appengine.api import users

from main.models import *


def list_greetings(request):
    guestbook_name = request.GET.get('guestbook_name') or ''
    greetings_query = Greeting.all().ancestor(
        guestbook_key(guestbook_name)).order('-date')
    greetings = greetings_query.fetch(10)

    if users.get_current_user():
        url = users.create_logout_url(request.path)
        url_linktext = 'Logout'
    else:
        url = users.create_login_url(request.path)
        url_linktext = 'Login'

    context = {
        'greetings': greetings,
        'url': url,
        'url_linktext': url_linktext,
        'guestbook_name': cgi.escape(guestbook_name),
        'guestbook_name_action': urllib.urlencode({'guestbook_name': guestbook_name})
    }
    
    return HttpResponse(get_template('index.html').render(Context(context)))

def create_greeting(request):
    if request.method == 'POST':
        # We set the same parent key on the 'Greeting' to ensure each greeting is in
        # the same entity group. Queries across the single entity group will be
        # consistent. However, the write rate to a single entity group should
        # be limited to ~1/second.
        guestbook_name = request.GET.get('guestbook_name')
        greeting = Greeting(parent=guestbook_key(guestbook_name))

        if users.get_current_user():
          greeting.author = users.get_current_user()

        greeting.content = request.POST.get('content')
        greeting.put()
    return HttpResponseRedirect('/?' + urllib.urlencode({'guestbook_name': guestbook_name}))

