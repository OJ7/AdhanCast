"""
Example on how to use the Media Controller
"""

import sys
import time

import pychromecast

def castMedia(cast_name, media_url):
    print('Casting ' + media_url + ' to ' + cast_name)

    chromecasts = pychromecast.get_listed_chromecasts(friendly_names=[cast_name])
    if not chromecasts:
        print('No chromecast with name "{}" discovered'.format(cast_name))
        sys.exit(1)

    cast = chromecasts[0]
    # Start socket client's worker thread and wait for initial status update
    cast.wait()

    cast.media_controller.play_media(media_url, "audio/mp3")

    # Wait for player_state PLAYING
    player_state = None
    t = 30
    while player_state != "PLAYING" and t > 0:
        try:
            if player_state != cast.media_controller.status.player_state:
                player_state = cast.media_controller.status.player_state

            time.sleep(0.1)
            t = t - 0.1
        except KeyboardInterrupt:
            break
