import pychromecast

casts = pychromecast.get_chromecasts()
if len(casts) == 0:
    print("No Devices Found")
    exit()

print("Found cast devices:")
for cast in casts:
    print(
        '  "{}" on {}:{} with UUID:{}'.format(
            cast.name, cast.host, cast.port, cast.uuid
        )
    )
