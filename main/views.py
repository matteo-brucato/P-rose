import os
import cgi
import datetime
import urllib
import json

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed
from django.template import Context, Template
from django.template.loader import get_template

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api.urlfetch import *

from main.models import *


def login(request):
    context = {}
    return HttpResponse(get_template('login.html').render(Context(context)))


def ClientLogin(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    # Execute POST request to Google ClientLogin
    post_data = request.POST
    for d in post_data:
        a = d.decode('utf-8')
        d = a.encode('ascii')
    result = fetch("https://www.google.com/accounts/ClientLogin",
        method = POST,
        payload = urllib.urlencode(post_data),
        headers = {'Content-type': 'application/x-www-form-urlencoded'},
        allow_truncated = False,
        follow_redirects = False,
        deadline = None,
        validate_certificate = None)
    # Check result and set response
    obj = {'Encoding': request.encoding}
    if result.status_code == 200:
        obj['Return'] = 0
    else:
        obj['Return'] = -1
    # Parse result and insert it into a dictionary to be returned as json
    for line in result.content.split('\n'):
        if line == '': continue
        pos = line.find('=')
        obj[line[0:pos]] = line[pos+1:]
    return HttpResponse(json.dumps(obj, indent=2), mimetype="text/plain")


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
    
    return HttpResponse(get_template('guestbook.html').render(Context(context)))


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

