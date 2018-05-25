# yet another better [adult swim] schedule
wanna seeee into the future?

## travis ci status
[![Build Status](https://travis-ci.org/SerCom-KC/adult-swim-schedule.svg?branch=source)](https://travis-ci.org/SerCom-KC/adult-swim-schedule)  
**make sure it says "build passing".** otherwise, you might looking at some outdated data. :P

## what is this?
created by [someone](https://github.com/SerCom-KC) using a little bit of [this](https://www.python.org/) and a little bit of [that](https://travis-ci.org/) on a bored-but-not-halloween evening.  
since the [original one](https://swimpedia.net/oldsched/) is under manual update mode at the moment, this project aims to make eveything back to automation again... maybe with archives of old schedules* as well?

\* as long as github allows us to do so

## but yours is not a human-readable web page!
i know, i know... i'll need some time before i can make that happen.  

## fine... but source?
[code](https://github.com/SerCom-KC/adult-swim-schedule/tree/source)!

## no, seriously, i mean the source of your schedule data!
okay... see this [line](https://github.com/SerCom-KC/adult-swim-schedule/blob/f1036dc86a5d6dbb3d3549b197fe6376795794d7/build.py#L29).  
did you see that `www.adultswim.com` thing? that's the official domain of [adult swim]!

## i'm a developer, how to use this api-like thing then?
all "responses" are valid json. add a `?` at the end of every url to make sure you are not being trolled by cached data.  
you should start from [https://github.com/SerCom-KC/adult-swim-schedule/raw/master/manifest](https://github.com/SerCom-KC/adult-swim-schedule/raw/master/manifest).  

### manifest
`updated` time of generation in unix timestamp  
`data` list of generated schedules  
- `date` schedule time in `YYYY-MM-DD` format
- `url` this is where you should go next

### actual schedule
please note that the schedule starts at night and ends at morning of the next day.

`date` same as above  
`data` list of shows  
- `show` title of the show
- `episode` name of the episode, (hopefully) with "a/an/the" in place
- `rating` sometimes it might be an empty string if someone forgets to do their job
- `airtime` time of the beginning of the block in unix timestamp

want more? impossible. that's already everything from official sources - at least, the known part of it.

## disclaimer
in no way affilliated with adult swim, cartoon network or it's parent companies or subsidiaries. schedule data is pulled from official xml sources and is correct at time of publication.  
**please do not contact any [adult swim] employee on social media regarding any schedule information listed here. treat any future schedule information as a placeholder until an official announcement is made.**

## license (for everything except schedule data)
```
This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://www.wtfpl.net/ for more details.
```
