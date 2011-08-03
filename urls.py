from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'main.views.list_greetings'),
    (r'^sign$', 'main.views.create_greeting'),
    (r'^login$', 'main.views.login'),
    (r'^ClientLogin$', 'main.views.ClientLogin'),
    # Example:
    # (r'^main/', include('main.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
