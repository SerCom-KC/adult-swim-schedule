#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import os
from datetime import datetime, date
from lxml import etree
import pytz
import re
import json
from calendar import monthrange

def getDate(month, day):
    if month == '01':
        date_str = 'January'
    elif month == '02':
        date_str = 'February'
    elif month == '03':
        date_str = 'March'
    elif month == '04':
        date_str = 'April'
    elif month == '05':
        date_str = 'May'
    elif month == '06':
        date_str = 'June'
    elif month == '07':
        date_str = 'July'
    elif month == '08':
        date_str = 'August'
    elif month == '09':
        date_str = 'September'
    elif month == '10':
        date_str = 'October'
    elif month == '11':
        date_str = 'November'
    elif month == '12':
        date_str = 'December'
    date_str += ' ' + day.lstrip('0')
    if int(day) >= 11 and int(day) <= 13:
        date_str += 'th'
    elif day.endswith('1'):
        date_str += 'st'
    elif day.endswith('2'):
        date_str += 'nd'
    elif day.endswith('3'):
        date_str += 'rd'
    else:
        date_str += 'th'
    return date_str

def getDoW(str):
    if str == '1':
        return 'Monday'
    elif str == '2':
        return 'Tuesday'
    elif str == '3':
        return 'Wednesday'
    elif str == '4':
        return 'Thursday'
    elif str == '5':
        return 'Friday'
    elif str == '6':
        return 'Saturday'
    elif str == '7':
        return 'Sunday'

def fixName(name, force_the=False):
    fixed_names = []
    for title in name.split('/'):
        fixed = re.sub(r'(.*?) $', 'The \\1', title)
        fixed = re.sub(r'(.*?), The$', 'The \\1', fixed)
        if force_the and not fixed.startswith('The '):
            fixed = 'The ' + fixed
        else:
            fixed = re.sub(r'(.*?), An$', 'An \\1', fixed)
            fixed = re.sub(r'(.*?), A$', 'A \\1', fixed)
        fixed_names.append(fixed)
    name = '/'.join(fixed_names)
    return name.replace('/', '; ')

def generate():
    s = requests.Session()
    today = datetime.now(pytz.timezone('US/Eastern'))
    day = int(today.strftime('%d').lstrip('0'))
    month = today.date().month
    schedules = []
    while True:
        url = 'https://www.adultswim.com/adultswimdynsched/asXml/' + str(day) + '.EST.xml'
        print('Fetching ' + url)
        allshows = etree.XML(s.get(url, timeout=3).content).xpath('//allshows/show')
        date_split = allshows[0].xpath('@date')[0].split('/')
        if int(date_split[0]) < month:
            print('\033[32mSchedule generation completed successfully!\033[0m')
            manifest(schedules)
            return 0
        date_str = date_split[2] + '-' + date_split[0] + '-' + date_split[1]
        as_shows = []
        for show in allshows:
            title = fixName(show.xpath('@title')[0])
            episodeName = fixName(show.xpath('@episodeName')[0])
            rating = show.xpath('@rating')[0]
            airtime_str = show.xpath('@date')[0] + ' ' + show.xpath('@military')[0]
            airtime_dt = pytz.timezone('US/Eastern').localize(datetime.strptime(airtime_str, '%m/%d/%Y %H:%M'))
            airtime = int(airtime_dt.timestamp())
            as_show = {"show": title, "episode": episodeName, "rating": rating, "airtime": airtime}
            as_shows.append(as_show)
        result = {"date": date_str, "data": as_shows}
        print('Writing schedule of ' + date_str + ' to file')
        file = open('master/' + date_str, 'w+')
        file.write(json.dumps(result))
        file.close()
        schedules.append(date_str)
        day += 1
        if day > monthrange(airtime_dt.date().year, airtime_dt.date().month)[1]:
            day = 1
            month = month + 1 if month != 12 else 1

def manifest(schedules):
    data = []
    for schedule in schedules:
        data.append({"date": schedule, "url": "https://github.com/" + os.environ['TRAVIS_REPO_SLUG'] + "/raw/master/" + schedule})
    result = {"updated": int(time.time()), "data": data}
    print('Writing to manifest')
    file = open('master/manifest', 'w+')
    file.write(json.dumps(result))
    file.close()
    print('\033[32mManifest generation completed successfully!\033[0m')

def webpage():
    file = open('master/manifest', 'r')
    schedules = json.loads(file.read())["data"]
    file.close()
    html_schedule = ''
    html_nav = ''
    html_gridtop = '<tr><td style="width: 75px; text-align: center; vertical-align: middle">TIME</td>'
    html_gridtimeslots = {
        "8:00PM": [], "8:15PM": [], "8:30PM": [], "8:45PM": [], 
        "9:00PM": [], "9:15PM": [], "9:30PM": [], "9:45PM": [], 
        "10:00PM": [], "10:15PM": [], "10:30PM": [], "10:45PM": [], 
        "11:00PM": [], "11:15PM": [], "11:30PM": [], "11:45PM": [], 
        "12:00AM": [], "12:15AM": [], "12:30AM": [], "12:45AM": [], 
        "1:00AM": [], "1:15AM": [], "1:30AM": [], "1:45AM": [], 
        "2:00AM": [], "2:15AM": [], "2:30AM": [], "2:45AM": [], 
        "3:00AM": [], "3:15AM": [], "3:30AM": [], "3:45AM": [], 
        "4:00AM": [], "4:15AM": [], "4:30AM": [], "4:45AM": [], 
        "5:00AM": [], "5:15AM": [], "5:30AM": [], "5:45AM": [], 
    }
    for schedule in schedules:
        date_split = schedule["date"].split('-')
        date_d = date(int(date_split[0]), int(date_split[1]), int(date_split[2]))
        html_schedule += '<div class="tab-pane fade" id="day' + str(date_d.day) + '">'
        html_nav += '<li><a data-toggle="pill" href="#day' + str(date_d.day) + '">' + getDoW(str(date_d.isoweekday())) + ', ' + getDate(date_split[1], date_split[2]) + '</a></li>'
        html_gridtop += '<td style="width: 150px; text-align: center; vertical-align: middle">' + getDoW(str(date_d.isoweekday())).upper() + ' ' + str(date_d.month) + '/' + str(date_d.day) + '</td>'
        if date_d.isoweekday() == 6:
            html_schedule += '<div class="alert alert-danger"><h4>Important:</h4><p>Please <b>do not</b> contact any Adult Swim employee on social media regarding any schedule information this page provides. <br>Treat any future Toonami schedule information as a placeholder until an official announcement is made.</p></div>'
        html_schedule += '<table class="table table-striped table-hover "><tbody>'
        file = open('master/' + schedule["date"], 'r')
        shows = json.loads(file.read())["data"]
        file.close()
        for index, show in enumerate(shows):
            time_dt = datetime.fromtimestamp(show['airtime']).astimezone(pytz.timezone('US/Eastern'))
            time_str = str(int(time_dt.strftime('%I'))) + time_dt.strftime(':%M%p')
            html_schedule += '<tr><td class="col-md-1 text-right vert-align"><b>' + time_str + '</b></td><td>' + show['show'] + '<br><small>"' + show['episode'] + '"</small></td><td class="col-md-2 vert-align">' + show['rating'] + '</td>'
            if show == shows[-1]:
                html_gridtimeslots[time_str].append({"show": show['show'], "episode": show['episode'], "color": None, "duration": int(time_dt.replace(hour=6, minute=0).timestamp()) - show['airtime']})
            else:
                html_gridtimeslots[time_str].append({"show": show['show'], "episode": show['episode'], "color": None, "duration": shows[index+1]['airtime'] - show['airtime']})
        html_schedule += '</tbody></table></div>'
    html = '<!DOCTYPE html><html><head><link rel="stylesheet" href="./bootstrap_min.css" media="screen"><script src="./jquery-3.2.1.min.js" type="text/javascript"></script><script src="./bootstrap.min.js" type="text/javascript"></script><title>yet another better [adult swim] schedule</title></head><div class="container"><div class="page-header" id="banner"><h1>yet another better [adult swim] schedule</h1><p class="lead">Wanna seeee into the future? // Last Update: ' + time.strftime('%B ') + time.strftime('%d, %Y at %H:%M:%S %Z').lstrip('0') + ' <img src="https://travis-ci.org/' + os.environ['TRAVIS_REPO_SLUG'] + '.svg?branch=' + os.environ['TRAVIS_BRANCH'] + '" alt="Build Status" /></p></div><div class="row"><div class="col-lg-3 col-md-4 col-sm-5"><ul class="nav nav-pills nav-stacked">'
    html_nav += '<li><a data-toggle="pill" href="#grid">Grid (Experimental)</a></li>'
    html += html_nav
    html += '</ul></div><div class="col-lg-9 col-md-8 col-sm-7 "><div id="schedule" class="tab-content">'
    html += html_schedule
    html += '<div class="tab-pane fade" id="grid" style="overflow-x: auto">'
    html += '<table class="table table-striped table-hover " style="width: ' + str((len(schedules) + 1) * 150) + 'px"><tbody>'
    html += html_gridtop
    for timeslot, shows in html_gridtimeslots.items():
        html += '<tr><td style="width: 75px; text-align: center; vertical-align: middle; font-weight: bold">' + timeslot.replace('AM', ' AM').replace('PM', ' PM') + '</td>'
        for show in shows:
            html += '<td style="width: 150px; text-align: center; vertical-align: middle" rowspan=' + str(int(show["duration"] / 900)) + ' title="' + show["episode"] + '">' + show["show"] + '</td>'
    html += '</tbody></table></div>'
    html += '</div></div></div><footer class="page-footer"><div class="row"><div class="col-lg-12"><p><a href="http://swimpedia.net/oldsched/" rel="nofollow">originally</a> created by <a href="http://twitter.com/jessfromabove" rel="nofollow">someone</a> using a little bit of <a href="http://getbootstrap.com" rel="nofollow">this</a> and a little bit of <a href="https://jquery.com/" rel="nofollow">that</a> on a bored halloween evening. colours by <a href="https://bootswatch.com/" rel="nofollow">tom</a>. </p><p>adapted by <a href="https://github.com/SerCom-KC" rel="nofollow">someone else</a> using a little bit of <a href="https://www.python.org/" rel="nofollow">this</a> and a little bit of <a href="https://travis-ci.org/" rel="nofollow">that</a> on a bored-but-not-halloween evening. source code available at <a href="https://github.com/' + os.environ['TRAVIS_REPO_SLUG'] + '" rel="nofollow">somewhere</a>. </p><p>bots? go <a href="./manifest" rel="nofollow">here</a>. still can\'t read it? ask your owner to read <a href="https://github.com/' + os.environ['TRAVIS_REPO_SLUG'] + '/blob/master/README.md#im-a-developer-how-to-use-this-api-like-thing-then" rel="nofollow">this</a>. </p><p>something weird happened? report it <a href="https://github.com/' + os.environ['TRAVIS_REPO_SLUG'] + '/issues/new" rel="nofollow">here</a>. </p><p>in no way affilliated with adult swim, cartoon network or it\'s parent companies or subsidiaries. schedule data is pulled from official xml sources and is correct at time of publication.</p><p>shout outs /r/adultswim, /r/toonami, /co/, toonamiarsenal, bumpworthy and myspleen. </p></div></div></footer></div></html>'
    file = open('master/index.html', 'w+')
    file.write(html)
    file.close()

if __name__ == "__main__":
    generate()
    webpage()
