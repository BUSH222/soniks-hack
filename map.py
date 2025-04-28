import numpy as np
from datetime import datetime
from beyond.io.tle import Tle
from beyond.dates import Date
from beyond.propagators.analytical.sgp4 import Sgp4


def get_satellite_tracks_from_tle(tle_str):
    tle = Tle(tle_str)
    orb = tle.orbit()
    orb = orb.propagate(Date(datetime.utcnow()))
    orb = orb.as_orbit(Sgp4())
    latitudes, longitudes = [], []
    prev_lon, prev_lat = None, None

    period = orb.infos.period
    start = orb.date - period

    orb.form = 'tle'
    stop = 2 * period
    step = period / 100

    for point in orb.ephemeris(start=start, stop=stop, step=step):
        point.frame = 'ITRF'
        point.form = 'spherical'
        lon, lat = np.degrees(point[1:3])
        if prev_lon is None:
            lons = []
            lats = []
            longitudes.append(lons)
            latitudes.append(lats)
        elif orb.i < np.pi / 2 and (np.sign(prev_lon) == 1 and np.sign(lon) == -1):
            lons.append(lon + 360)
            lats.append(lat)
            lons = [prev_lon - 360]
            lats = [prev_lat]
            longitudes.append(lons)
            latitudes.append(lats)
        elif orb.i > np.pi/2 and (np.sign(prev_lon) == -1 and np.sign(lon) == 1):
            lons.append(lon - 360)
            lats.append(lat)
            lons = [prev_lon + 360]
            lats = [prev_lat]
            longitudes.append(lons)
            latitudes.append(lats)

        lons.append(lon)
        lats.append(lat)
        prev_lon = lon
        prev_lat = lat

    # img = "/Users/tedvtorov/Desktop/py-proj/new/soniks-hack/image.png"

    # im = plt.imread(str(img))
    # plt.figure(figsize=(15.2, 8.2))
    # plt.imshow(im, extent=[-180, 180, -90, 90])

    # for lons, lats in zip(longitudes, latitudes):
    #     plt.plot(lons, lats, 'r')

    lon, lat = np.degrees(orb.copy(frame='ITRF', form='spherical')[1:3])
    # plt.plot([lon], [lat], 'ro')

    # plt.xlim([-180, 180])
    # plt.ylim([-90, 90])
    # plt.grid(True, color='w', linestyle=":", alpha=0.4)
    # plt.xticks(range(-180, 181, 30))
    # plt.yticks(range(-90, 91, 30))
    # plt.tight_layout()

    # if "no-display" not in sys.argv:
    #     plt.show()

    return [longitudes, latitudes, [lon, lat]]


if __name__ == "__main__":
    tle_str = """METEOR M2-4
    1 59051U 24039A   25118.15566969  .00000086  00000-0  58284-4 0  9997
    2 59051  98.6463  79.0897 0006030 296.7745  63.2816 14.22361028 60266"""

    get_satellite_tracks_from_tle(tle_str)
