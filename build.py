#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import os
from datetime import datetime, date
import pytz
import re
import json

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
    schedules = []

    # JSON schedule
    json_days_limit = 30
    url = "https://www.adultswim.com/api/schedule/onair"
    while True:
        try:
            json_past = s.get(url, params={"days": 0 - json_days_limit}, timeout=30).json()
            json_future = s.get(url, params={"days": json_days_limit}, timeout=30).json()
            break
        except Exception:
            continue
    if json_past["status"] != "ok" or json_future["status"] != "ok": return -1
    json_showings = json_past["data"] + json_future["data"]
    if json_showings == []: return -1
    as_schedules = {}
    for json_showing in json_showings:
        title = json_showing["showTitle"].strip()
        episodeName = json_showing["episodeTitle"]
        rating = json_showing.get("rating", "").replace(" ", "") # https://web.archive.org/web/20190113153055id_/https://www.adultswim.com/api/schedule/onair?days=7 (Dragon Ball Super - The Evil Emperor Returns! A Reception from Mysterious Assassins?! at 11pm on Jan 19)
        airtime_dt = pytz.timezone("US/Eastern").localize(datetime.strptime(json_showing["datetime"][:19], '%Y-%m-%dT%H:%M:%S'))
        airtime = int(airtime_dt.timestamp())
        as_show = {"show": title, "episode": episodeName, "rating": rating, "airtime": airtime}
        date_str = json_showing["date"][:10]
        if date_str not in as_schedules:
            as_schedules[date_str] = [as_show]
        else if as_show not in as_schedules[date_str]:
            as_schedules[date_str].append(as_show)

    for date_str in as_schedules.keys():
        as_shows = as_schedules[date_str]
        result = {"date": date_str, "data": as_shows}
        print('Writing schedule of %s to file' % (date_str))
        with open('master/' + date_str, 'w+') as file:
            json.dump(result, file)
        schedules.append(date_str)

    print('\033[32mSchedule generation completed successfully!\033[0m')
    manifest(schedules)
    return 0

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
    for schedule in schedules:
        date_split = schedule["date"].split('-')
        date_d = date(int(date_split[0]), int(date_split[1]), int(date_split[2]))
        html_schedule += '<div class="tab-pane fade" id="day' + str(date_d.day) + '">'
        html_nav += '<li><a data-toggle="pill" href="#day' + str(date_d.day) + '">' + getDoW(str(date_d.isoweekday())) + ', ' + getDate(date_split[1], date_split[2]) + '</a></li>'
        if date_d.isoweekday() == 6:
            html_schedule += '<div class="alert alert-danger"><h4>Important:</h4><p>Please <b>do not</b> contact any Adult Swim employee on social media regarding any schedule information this page provides. <br>Treat any future Toonami schedule information as a placeholder until an official announcement is made.</p></div>'
        html_schedule += '<table class="table table-striped table-hover "><tbody>'
        file = open('master/' + schedule["date"], 'r')
        shows = json.loads(file.read())["data"]
        file.close()
        for index, show in enumerate(shows):
            time_dt = datetime.fromtimestamp(show['airtime']).astimezone(pytz.timezone('US/Eastern'))
            time_str = str(int(time_dt.strftime('%I'))) + time_dt.strftime(':%M') + time_dt.strftime('%p').lower()
            html_schedule += '<tr><td class="col-md-1 text-right vert-align"><b>' + time_str + '</b></td><td>' + show['show'] + '<br><small>"' + show['episode'] + '"</small></td><td class="col-md-2 vert-align">' + show['rating'] + '</td>'
        html_schedule += '</tbody></table></div>'
    html = '<!DOCTYPE html><html><head><link rel="stylesheet" href="./bootstrap_min.css" media="screen"><script src="./jquery-3.2.1.min.js" type="text/javascript"></script><script src="./bootstrap.min.js" type="text/javascript"></script><title>yet another normal [adult swim] schedule</title></head><div class="container"><div class="page-header" id="banner"><h1>yet another normal [adult swim] schedule</h1><p class="lead">There is no "future" // Last Update: ' + time.strftime('%B ') + time.strftime('%d, %Y at %H:%M:%S %Z').lstrip('0') + ' <img src="https://travis-ci.org/' + os.environ['TRAVIS_REPO_SLUG'] + '.svg?branch=' + os.environ['TRAVIS_BRANCH'] + '" alt="Build Status" /></p></div><div class="row"><div class="col-lg-3 col-md-4 col-sm-5"><ul class="nav nav-pills nav-stacked">'
    html += html_nav
    html += '</ul></div><div class="col-lg-9 col-md-8 col-sm-7 "><div id="schedule" class="tab-content">'
    html += html_schedule
    html += '</div></div></div><footer class="page-footer"><div class="row"><div class="col-lg-12"><p><a href="http://swimpedia.net/oldsched/" rel="nofollow">originally</a> created by <a href="http://twitter.com/jessfromabove" rel="nofollow">someone</a> using a little bit of <a href="http://getbootstrap.com" rel="nofollow">this</a> and a little bit of <a href="https://jquery.com/" rel="nofollow">that</a> on a bored halloween evening. colours by <a href="https://bootswatch.com/" rel="nofollow">tom</a>. </p><p>adapted by <a href="https://github.com/SerCom-KC" rel="nofollow">someone else</a> using a little bit of <a href="https://www.python.org/" rel="nofollow">this</a> and a little bit of <a href="https://travis-ci.org/" rel="nofollow">that</a> on a bored-but-not-halloween evening. source code available at <a href="https://github.com/' + os.environ['TRAVIS_REPO_SLUG'] + '" rel="nofollow">somewhere</a>. </p><p>bots? go <a href="./manifest" rel="nofollow">here</a>. still can\'t read it? ask your owner to read <a href="https://github.com/' + os.environ['TRAVIS_REPO_SLUG'] + '/blob/master/README.md#im-a-developer-how-to-use-this-api-like-thing-then" rel="nofollow">this</a>. </p><p>something weird happened? report it <a href="https://github.com/' + os.environ['TRAVIS_REPO_SLUG'] + '/issues/new" rel="nofollow">here</a>. </p><p>in no way affilliated with adult swim, cartoon network or it\'s parent companies or subsidiaries. schedule data is pulled from official json and/or xml sources and is correct at time of publication.</p><p>shout outs /r/adultswim, /r/toonami, /co/, toonamiarsenal, bumpworthy and myspleen. </p></div></div></footer></div></html>'
    file = open('master/index.html', 'w+')
    file.write(html)
    file.close()

if __name__ == "__main__":
    generate()
    webpage()
