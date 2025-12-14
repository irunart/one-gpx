'''
Usage:
  gpx_mockup_time.py <input_gpx> <output_gpx> 
  gpx_mockup_time.py <input_gpx> <output_gpx> <mockup_time_start> <mockup_speed_meters_per_second> <track_name>

Options:
  -h help
  -v version
'''

# Example usage:
# %python gpx_mockup_time.py compare-hk100/2025HK100.gpx compare-hk100/hk100-mockup.gpx '2025-01-01 08:08:01 +08:00' 1.38 'HK100 mockup'

import docopt
import logging
import gpxpy 
import gpxpy.gpx
from gpxpy import geo
from datetime import timedelta
from dateutil import parser as dt_parser
from gpxpy import geo

DEFAULT_START_TIME_BASIC_MODE = dt_parser.parse('9999-12-15 0:0:1 +08:00')

def mockup_time_basic(reverse=False):
    if not hasattr(mockup_time_basic, '_last_mockup_time'):
        mockup_time_basic._last_mockup_time = DEFAULT_START_TIME_BASIC_MODE
    if reverse:
        mockup_time_basic._last_mockup_time -= timedelta(seconds=1)
    else:
        mockup_time_basic._last_mockup_time += timedelta(seconds=1)
    return mockup_time_basic._last_mockup_time

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    arguments = docopt.docopt(__doc__)

    gpx_file = open(arguments['<input_gpx>'], 'r') 
    gpx = gpxpy.parse(gpx_file)
    print('Finished loading GPX')
    print(gpx)

    mockup_time_start = arguments['<mockup_time_start>']
    mockup_speed_meters_per_second = arguments['<mockup_speed_meters_per_second>']
    track_name = arguments['<track_name>']
    if mockup_time_start and mockup_speed_meters_per_second:
        # Advanced mode
        mockup_speed_meters_per_second = float(mockup_speed_meters_per_second)
        print('[Advanced] Processing mockup time.')
        cur_time = dt_parser.parse(mockup_time_start)
        gpx.name = track_name
        last_point = None
        for track in gpx.tracks:
            track.name = track_name
            for segment in track.segments:
                for point in segment.points:
                    if last_point is None:
                        pass
                    else:
                        dist = geo.haversine_distance(point.latitude, point.longitude, last_point.latitude, last_point.longitude)
                        delta_time = timedelta(seconds=(dist / mockup_speed_meters_per_second))
                        cur_time += delta_time
                        # print(delta_time)
                    point.time = cur_time
                    last_point = point
    else:
        # Basic mode
        print('[Basic] Processing mockup time.')
        gpx.time = DEFAULT_START_TIME_BASIC_MODE
        for track in gpx.tracks:
            track.name = track_name
            for segment in track.segments:
                for point in segment.points:
                    point.time = mockup_time_basic()
    c = open(arguments['<output_gpx>'], 'w').write(gpx.to_xml())
    print(f'Write {c} chars to new GPX {arguments["<output_gpx>"]}')

