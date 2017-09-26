from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError

from .models import *
from .forms import *

import os
import json
import datetime
import requests
import itertools
import urllib.request
import urllib.parse

def get_access_token():
    access_token = json.loads(requests.get(
        "https://graph.facebook.com/oauth/access_token?client_id=" + os.environ.get('APP_ID') + "&client_secret=" + os.environ.get('APP_SECRET')  + "&grant_type=client_credentials").content.decode('utf-8'))['access_token']
    return access_token

def get_events_particular(host_type):
    batch_values = []
    events = []
    event_hosts = EventHost.objects.filter(event_type__in=host_type)

    for host in event_hosts:
        batch_values.append({"method": "GET", "relative_url": host.host_id + "/?fields=events{cover,name,attending_count,interested_count,start_time,end_time,place}"})

    url = "https://graph.facebook.com"
    access_token = get_access_token()

    values = {"access_token":access_token, "batch":batch_values, "include_headers": "false"}

    data = urllib.parse.urlencode(values)
    data = data.encode('utf-8')

    req = urllib.request.Request(url, data)
    resp = urllib.request.urlopen(req)
    respData = resp.readall().decode('utf-8')
    result = json.loads(respData)

    for event in result:
        events.append(json.loads(event['body'])['events']['data'])

    events = list(itertools.chain.from_iterable(events))    


    return events

def get_hosts_particular(host_type):
    batch_values = []
    events = []
    event_hosts = EventHost.objects.filter(host_type__in=host_type)

    for host in event_hosts:
        batch_values.append({"method": "GET", "relative_url": host.host_id + "/?fields=events{cover,name,attending_count,interested_count,start_time,end_time,place}"})

    url = "https://graph.facebook.com"
    access_token = get_access_token()

    values = {"access_token":access_token, "batch":batch_values, "include_headers": "false"}

    data = urllib.parse.urlencode(values)
    data = data.encode('utf-8')

    req = urllib.request.Request(url, data)
    resp = urllib.request.urlopen(req)
    respData = resp.readall().decode('utf-8')
    result = json.loads(respData)

    for event in result:
        events.append(json.loads(event['body'])['events']['data'])

    events = list(itertools.chain.from_iterable(events))    


    return events

def index(request):

    events = get_events_particular(['Live Shows', 'Art Exhibition', 'Craft Market'])

    date_today = datetime.date.today()
    week_day = date_today.weekday()

    if (week_day == 0 or week_day == 1 or week_day == 2 or week_day == 3 or week_day == 4):
        weekend_start = date_today + datetime.timedelta(days=4-week_day)
        weekend_stop = weekend_start + datetime.timedelta(days=2)
        mid_weekend = weekend_start + datetime.timedelta(days=1)
    else:
        weekend_start = date_today
        weekend_stop = weekend_start + datetime.timedelta(days=6-week_day)
        mid_weekend = weekend_start

    return render(request, 'index.html', {"events": events, "date": datetime.datetime.now().strftime('%Y-%m-%dT00:00:00+0200'), "weekend_start": weekend_start, "weekend_stop": weekend_stop, "mid_weekend": mid_weekend, "date_today": date_today})

def event_detail(request, event_id):

    access_token = get_access_token()

    event = json.loads(requests.get(
        "https://graph.facebook.com/" + event_id + "/?fields=cover,name,description,attending_count,interested_count,start_time,end_time,place&access_token=" + access_token).content.decode('utf-8'))
        
    try:
        event['name']
    except KeyError:
        raise Http404("event does not exist on Rock Worthy") 
        
    return render(request, 'Events/event_detail.html', {'event': event})


def venues(request):
    hosts = []
    access_token = get_access_token()

    event_hosts = EventHost.objects.filter(host_type='Venue')

    for event in event_hosts:
        result = json.loads(requests.get(
            "https://graph.facebook.com/" + str(event.host_id) + "/?fields=fan_count,picture,category,name&access_token=" + access_token).content.decode('utf-8'))
        hosts.append(result)       
    
    hosts = sorted(hosts, key=lambda k: k['fan_count'], reverse=True) 

    return render(request, 'Venues/venues.html', {"hosts": hosts})


def venue_detail(request, venue_id):

    event_host = EventHost.objects.filter(host_id=venue_id)[0]

    access_token = get_access_token()

    venue = json.loads(requests.get(
        "https://graph.facebook.com/" + venue_id + "/?fields=cover,events{cover,name,place,attending_count,interested_count,start_time,end_time},fan_count,picture,category,name&access_token=" + access_token).content.decode('utf-8'))

    try:
        venue['id']
    except KeyError:
        raise Http404("Venue does not exists on Rock Worthy")

    return render(request, 'Venues/venue_detail.html', {"venue": venue, "event_host": event_host, "date": datetime.datetime.now().strftime('%Y-%m-%dT00:00:00+0200')})

def live_music(request):

    events = get_events_particular(['Live Shows'])

    date_today = datetime.date.today()
    week_day = date_today.weekday()

    if (week_day == 0 or week_day == 1 or week_day == 2 or week_day == 3 or week_day == 4):
        weekend_start = date_today + datetime.timedelta(days=4-week_day)
        weekend_stop = weekend_start + datetime.timedelta(days=2)
        mid_weekend = weekend_start + datetime.timedelta(days=1)
    else:
        weekend_start = date_today
        weekend_stop = weekend_start + datetime.timedelta(days=6-week_day)
        mid_weekend = weekend_start

    return render(request, 'Events/livemusic.html', {"events": events, "date": datetime.datetime.now().strftime('%Y-%m-%dT00:00:00+0200'), "weekend_start": weekend_start, "weekend_stop": weekend_stop, "mid_weekend": mid_weekend, "date_today": date_today})

def art_exhibition(request):

    date_today = datetime.date.today()
    week_day = date_today.weekday()

    if (week_day == 0 or week_day == 1 or week_day == 2 or week_day == 3 or week_day == 4):
        weekend_start = date_today + datetime.timedelta(days=4-week_day)
        weekend_stop = weekend_start + datetime.timedelta(days=2)
        mid_weekend = weekend_start + datetime.timedelta(days=1)
    else:
        weekend_start = date_today
        weekend_stop = weekend_start + datetime.timedelta(days=6-week_day)
        mid_weekend = weekend_start
    events = get_events_particular(['Art Exhibition'])

    return render(request, 'Events/artexhibitions.html', {"events": events, "date": datetime.datetime.now().strftime('%Y-%m-%dT00:00:00+0200'), "weekend_start": weekend_start, "weekend_stop": weekend_stop, "mid_weekend": mid_weekend, "date_today": date_today})

def craft_market(request):

    date_today = datetime.date.today()
    week_day = date_today.weekday()

    if (week_day == 0 or week_day == 1 or week_day == 2 or week_day == 3 or week_day == 4):
        weekend_start = date_today + datetime.timedelta(days=4-week_day)
        weekend_stop = weekend_start + datetime.timedelta(days=2)
        mid_weekend = weekend_start + datetime.timedelta(days=1)
    else:
        weekend_start = date_today
        weekend_stop = weekend_start + datetime.timedelta(days=6-week_day)
        mid_weekend = weekend_start

    events = get_events_particular(['Craft Market'])

    return render(request, 'Events/craftmarkets.html', {"events": events, "date": datetime.datetime.now().strftime('%Y-%m-%dT00:00:00+0200'), "weekend_start": weekend_start, "weekend_stop": weekend_stop, "mid_weekend": mid_weekend, "date_today": date_today})

def special_events(request):

    date_today = datetime.date.today()
    week_day = date_today.weekday()

    if (week_day == 0 or week_day == 1 or week_day == 2 or week_day == 3 or week_day == 4):
        weekend_start = date_today + datetime.timedelta(days=4-week_day)
        weekend_stop = weekend_start + datetime.timedelta(days=2)
        mid_weekend = weekend_start + datetime.timedelta(days=1)
    else:
        weekend_start = date_today
        weekend_stop = weekend_start + datetime.timedelta(days=6-week_day)
        mid_weekend = weekend_start

    events = get_hosts_particular(['Special Event'])

    return render(request, 'Events/special_events.html', {"events": events, "date": datetime.datetime.now().strftime('%Y-%m-%dT00:00:00+0200'), "weekend_start": weekend_start, "weekend_stop": weekend_stop, "mid_weekend": mid_weekend, "date_today": date_today})


def contact(request):
    if request.method == 'POST':
        form = Query(request.POST)

        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            query = form.cleaned_data['query']

            try:
                send_mail('rockworthy.co.za Query', 'email: ' + email + '\n\nclient name: ' + name + '\n\nclient query: \n\n' + query, 'query@rockworthy.co.za', ['info@rockworthy.co.za'])
            except BadHeaderError:
                return HttpResponse('Invalid Header found.')

            messages.success(request, 'Thank you for your query! Your query has been sent. We will contact you as soon as possible.')
            return HttpResponseRedirect('/contact/') 
    else:
        form = Query()
    return render(request, 'contact.html', {'form': form})

def about(request):

    return render(request, 'about.html')

