#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import os
from datetime import datetime
from lxml import etree
import pytz
import re
import json
from calendar import monthrange

def getDate(month, day):
    if month == '01':
        date = 'January'
    elif month == '02':
        date = 'February'
    elif month == '03':
        date = 'March'
    elif month == '04':
        date = 'April'
    elif month == '05':
        date = 'May'
    elif month == '06':
        date = 'June'
    elif month == '07':
        date = 'July'
    elif month == '08':
        date = 'August'
    elif month == '09':
        date = 'September'
    elif month == '10':
        date = 'October'
    elif month == '11':
        date = 'November'
    elif month == '12':
        date = 'December'
    date += ' ' + day.lstrip('0')
    if int(day) >= 11 and int(day) <= 13:
        date += 'th'
    elif day.endswith('1'):
        date += 'st'
    elif day.endswith('2'):
        date += 'nd'
    elif day.endswith('3'):
        date += 'rd'
    else:
        date += 'th'
    return date

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

def fixName(name):
    for title in name.split('/'):
        fixed = re.sub(r'(.*?) $', 'The \\1', title)
        fixed = re.sub(r'(.*?), The$', 'The \\1', fixed)
        fixed = re.sub(r'(.*?), An$', 'An \\1', fixed)
        fixed = re.sub(r'(.*?), A$', 'A \\1', fixed)
        name = name.replace(title, fixed)
    return name.replace('/', '; ')

def generate():
    global html_schedule
    global html_nav
    today = datetime.now(pytz.timezone('US/Eastern'))
    day = int(today.strftime('%d').lstrip('0'))
    month = today.date().month
    schedules = []
    while True:
        url = 'https://www.adultswim.com/adultswimdynsched/asXml/' + str(day) + '.EST.xml'
        print('Fetching ' + url)
        allshows = etree.XML(requests.get(url, timeout=10).content).xpath('//allshows/show')
        date_split = allshows[0].xpath('@date')[0].split('/')
        if int(date_split[0]) < month:
            print('\033[32mSchedule generation completed successfully!\033[0m')
            manifest(schedules)
            return 0
        date = date_split[2] + '-' + date_split[0] + '-' + date_split[1]
        as_shows = []
        html_schedule += '<div class="tab-pane fade" id="day' + str(day) + '">'
        html_nav += '<li><a data-toggle="pill" href="#day' + str(day) + '">' + getDoW(allshows[0].xpath('@weekday')[0]) + ', ' + getDate(date_split[0], date_split[1]) + '</a></li>'
        if allshows[0].xpath('@weekday')[0] == '6':
            html_schedule += '<div class="alert alert-danger"><h4>Important:</h4><p>Please <b>do not</b> contact any Adult Swim employee on social media regarding any schedule information this page provides. <br>Treat any future Toonami schedule information as a placeholder until an official announcement is made.</p></div>'
        html_schedule += '<table class="table table-striped table-hover "><tbody>'
        for show in allshows:
            title = fixName(show.xpath('@title')[0])
            episodeName = fixName(show.xpath('@episodeName')[0])
            rating = show.xpath('@rating')[0]
            airtime_str = show.xpath('@date')[0] + ' ' + show.xpath('@military')[0]
            airtime_dt = pytz.timezone('US/Eastern').localize(datetime.strptime(airtime_str, '%m/%d/%Y %H:%M'))
            airtime = int(airtime_dt.timestamp())
            as_show = {"show": title, "episode": episodeName, "rating": rating, "airtime": airtime}
            as_shows.append(as_show)
            html_schedule += '<tr><td class="col-md-1 text-right vert-align"><b>' + show.xpath('@time')[0].replace('.', '').replace(' ', '') + '</b></td><td>' + title + '<br><small>"' + episodeName + '"</small></td><td class="col-md-2 vert-align">' + rating + '</td>'
        html_schedule += '</tbody></table></div>'
        result = {"date": date, "data": as_shows}
        print('Writing schedule of ' + date + ' to file')
        file = open('master/' + date, 'w+')
        file.write(json.dumps(result))
        file.close()
        schedules.append(date)
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
    global html_schedule
    global html_nav
    html = '<!DOCTYPE html><html><head><link rel="stylesheet" href="./bootstrap_min.css" media="screen"><script src="./jquery-3.2.1.min.js" type="text/javascript"></script><script src="./bootstrap.min.js" type="text/javascript"></script><title>better [adult swim] schedule</title></head><div class="container"><div class="page-header" id="banner"><h1>better [adult swim] schedule</h1><p class="lead">Wanna seeee into the future? // Last Update: ' + time.strftime('%B ') + time.strftime('%d, %Y at %H:%M:%S %Z').lstrip('0') + ' <img src="https://travis-ci.org/' + os.environ['TRAVIS_REPO_SLUG'] + '.svg?branch=' + os.environ['TRAVIS_BRANCH'] + '" alt="Build Status" /></p></div><div class="row"><div class="col-lg-3 col-md-4 col-sm-5"><ul class="nav nav-pills nav-stacked">'
    html += html_nav
    html += '</ul></div><div class="col-lg-9 col-md-8 col-sm-7 "><div id="schedule" class="tab-content">'
    html += html_schedule
    html += '</div></div></div><footer class="page-footer"><div class="row"><div class="col-lg-12"><p>originally created by <a href="http://twitter.com/jessfromabove" rel="nofollow">someone</a> using a little bit of <a href="http://getbootstrap.com" rel="nofollow">this</a> and a little bit of <a href="https://jquery.com/" rel="nofollow">that</a> on a bored halloween evening. colours by <a href="https://bootswatch.com/" rel="nofollow">tom</a>. </p><p>adapted by <a href="https://github.com/SerCom-KC" rel="nofollow">someone else</a> using a little bit of <a href="https://www.python.org/" rel="nofollow">this</a> and a little bit of <a href="https://travis-ci.org/" rel="nofollow">that</a> on a bored-but-not-halloween evening. source code available at <a href="https://github.com/' + os.environ['TRAVIS_REPO_SLUG'] + '" rel="nofollow">github</a>. </p><p>bots? go <a href="./manifest" rel="nofollow">here</a>. still can\'t read it? ask your owner to read <a href="https://github.com/' + os.environ['TRAVIS_REPO_SLUG'] + '/blob/master/README.md#im-a-developer-how-to-use-this-api-like-thing-then" rel="nofollow">this</a>. </p><p>in no way affilliated with adult swim, cartoon network or it\'s parent companies or subsidiaries. schedule data is pulled from official xml sources and is correct at time of publication.</p><p>shout outs /r/adultswim, /r/toonami, /co/, toonamiarsenal, bumpworthy and myspleen. </p></div></div></footer></div></html>'
    file = open('master/index.html', 'w+')
    file.write(html)
    file.close()

if __name__ == "__main__":
    global html_schedule
    global html_nav
    html_schedule = ''
    html_nav = ''
    generate()
    webpage()
