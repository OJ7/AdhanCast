"""
Example on how to use the YouTube Controller

"""

import argparse
import logging
import sys

import pychromecast
from pychromecast.controllers.youtube import YouTubeController

def castYoutube(cast_name, video_id):
    print('Casting http://youtube.com/watch?v=' + video_id + ' to ' + cast_name)
    chromecasts = pychromecast.get_listed_chromecasts(friendly_names=[cast_name])
    if not chromecasts:
        print('No chromecast with name "{}" discovered'.format(cast_name))
        sys.exit(1)

    cast = chromecasts[0]
    # Start socket client's worker thread and wait for initial status update
    cast.wait()

    yt = YouTubeController()
    cast.register_handler(yt)
    yt.play_video(video_id)
    return True