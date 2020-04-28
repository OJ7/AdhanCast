import sys
import traceback
import json
import threading
from datetime import datetime, time as timeCopy
import sched, time
import urllib.parse
from urllib.request import Request, urlopen
from cast_youtube import castYoutube
from cast_media import castMedia
import vlc
from apscheduler.schedulers.background import BackgroundScheduler

from global_vars import city, country, calculation_method, cast_device_name, adhan_mp3, fajr_adhan_mp3, adhan_youtube_video_id, fajr_adhan_youtube_video_id

SCAN_INTERVAL = 1 * 60 * 60 # number of seconds between updates (i.e. 1 hour)

# prayer times
fajr = None
sunrise = None
dhuhr = None
asr = None
maghrib = None
isha = None

# Used to play Adhan on local device
regAdhanPlayer = vlc.MediaPlayer(adhan_mp3)
fajrAdhanPlayer = vlc.MediaPlayer(fajr_adhan_mp3)

lastUpdated = None

# scheduled adhan jobs (currently unused)
fajrJob = None
dhuhrJob = None
asrJob = None
maghribJob = None
ishaJob = None

def getHoursFromStr(timeStr):
    return int(timeStr[:2])

def getMinutesFromStr(timeStr):
    return int(timeStr[-2:])

def hasPrayerTimePassed(prayerTimeStr):
    # convert hh:mm to seconds
    prayerTime = getHoursFromStr(prayerTimeStr) * 3600 + getMinutesFromStr(prayerTimeStr) * 60

    # current time in seconds
    now = datetime.now()
    now = now.hour * 3600 + now.minute * 60 + now.second

    return now > prayerTime

def scheduleAdhan(prayerTimeStr, isFajr):
    schedDate = datetime.now().date()
    schedTime = timeCopy(getHoursFromStr(prayerTimeStr), getMinutesFromStr(prayerTimeStr))
    scheduledTime = datetime.combine(schedDate, schedTime)
    adhanPlayer = fajrAdhanPlayer if isFajr else regAdhanPlayer
    return scheduler.add_job(adhanPlayer.play, 'date', run_date=scheduledTime, args=[])

    # NOTE: Casting from YouTube only works for ChromeCast devices (not smart speakers like Google Home)
    # videoId = fajr_adhan_youtube_video_id if isFajr else adhan_youtube_video_id
    # return scheduler.add_job(castYoutube, 'date', run_date=scheduledTime, args=[cast_device_name, videoId])

def scheduleAdhanCastForToday():
    if scheduler.running:
        scheduler.shutdown(wait=True)

    if not hasPrayerTimePassed(fajr):
        print('Scheduling Fajr')
        fajrJob = scheduleAdhan(fajr, True)

    if not hasPrayerTimePassed(dhuhr):
        print('Scheduling Dhuhr')
        dhuhrJob = scheduleAdhan(dhuhr, False)

    if not hasPrayerTimePassed(asr):
        print('Scheduling Asr')
        asrJob = scheduleAdhan(asr, False)

    if not hasPrayerTimePassed(maghrib):
        print('Scheduling Maghrib')
        maghribJob = scheduleAdhan(maghrib, False)

    if not hasPrayerTimePassed(isha):
        print('Scheduling Isha')
        ishaJob = scheduleAdhan(isha, False)

    scheduler.start()

def needsUpdate():
    # update if prayer times missing, or if a new day has started
    return None in [fajr, dhuhr, asr, maghrib, isha, lastUpdated] or (datetime.now().date() > lastUpdated)

def updatePrayerTimes():
    threading.Timer(SCAN_INTERVAL, updatePrayerTimes).start()

    if not needsUpdate():
        return False

    print ('\nUpdating Salat times')

    url = 'http://api.aladhan.com/v1/timingsByCity?city=' + urllib.parse.quote(city) + '&country=' + urllib.parse.quote(country) + '&method=' + calculation_method

    req = Request(url)
    req.add_header('Accept', 'application/json')
    req.add_header('Content-Type', 'application/json')
    req.add_header('User-Agent', 'Magic Browser')
    response = urlopen(req).read().decode('utf-8')

    jsonString = json.loads(response)

    times = jsonString['data']['timings']

    global fajr
    global sunrise
    global dhuhr
    global asr
    global maghrib
    global isha
    global lastUpdated

    fajr = times['Fajr']
    sunrise = times['Sunrise']
    dhuhr = times['Dhuhr']
    asr = times['Asr']
    maghrib = times['Maghrib']
    isha = times['Isha']
    lastUpdated = datetime.now()

    print(lastUpdated.strftime("%b-%d-%Y %H:%M:%S"))
    print('+---------+-------+')
    print('|   Fajr  | ' + fajr + ' |')
    print('| Sunrise | ' + sunrise + ' |')
    print('|  Dhuhr  | ' + dhuhr + ' |')
    print('|   Asr   | ' + asr + ' |')
    print('| Maghrib | ' + maghrib + ' |')
    print('|   Isha  | ' + isha + ' |')
    print('+---------+-------+')

    scheduleAdhanCastForToday()

def setup():
    global scheduler
    scheduler = BackgroundScheduler()

    try:
        updatePrayerTimes()
    except Exception as error:
        traceback.print_exc()
    return True

setup()