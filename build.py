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

def fixName(name):
    for title in name.split('/'):
        fixed = re.sub(r'(.*?) $', 'The \\1', title)
        fixed = re.sub(r'(.*?), The$', 'The \\1', fixed)
        fixed = re.sub(r'(.*?), An$', 'An \\1', fixed)
        fixed = re.sub(r'(.*?), A$', 'A \\1', fixed)
        name = name.replace(title, fixed)
    return name.replace('/', '; ')

def generate():
    today = datetime.now(pytz.timezone('US/Eastern'))
    day = int(today.strftime('%d').lstrip('0'))
    month = today.date().month
    while True:
        url = 'https://www.adultswim.com/adultswimdynsched/asXml/' + str(day) + '.EST.xml'
        print('Fetching ' + url)
        allshows = etree.XML(requests.get(url, timeout=10).content).xpath('//allshows/show')
        date_split = allshows[0].xpath('@date')[0].split('/')
        date = date_split[2] + '-' + date_split[0] + '-' + date_split[1]
        as_shows = []
        for show in allshows:
            title = fixName(show.xpath('@title')[0])
            episodeName = fixName(show.xpath('@episodeName')[0])
            rating = show.xpath('@rating')[0]
            airtime_str = show.xpath('@date')[0] + ' ' + show.xpath('@military')[0]
            airtime_dt = pytz.timezone('US/Eastern').localize(datetime.strptime(airtime_str, '%m/%d/%Y %H:%M'))
            if airtime_dt.date().month < month:
                print('\033[32mSchedule generation completed successfully!\033[0m')
                return 0
            airtime = int(airtime_dt.timestamp())
            as_show = {"show": title, "episode": episodeName, "rating": rating, "airtime": airtime}
            as_shows.append(as_show)
        result = {"date": date, "data": as_shows}
        print('Writing schedule of ' + date + ' to file')
        file = open('master/' + date, 'w+')
        file.write(json.dumps(result))
        file.close()
        day += 1
        if day > monthrange(airtime_dt.date().year, airtime_dt.date().month)[1]:
            day = 1
            month = month + 1 if month != 12 else 1

if __name__ == "__main__":
    generate()
