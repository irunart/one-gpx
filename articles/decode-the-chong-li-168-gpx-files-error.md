# Decode the Chong Li 168 GPX files error

- **Original Link**: https://hash.hupili.net/decode-the-chong-li-168-gpx-files-error
- **Last Fetch Time**: 2025-12-08
- **Author**: hupili
- **Tags**: gpx, trail running, chong li 168, data processing

## Summary

This article discusses the issues encountered with the GPX files provided by the Chong Li 168 trail race. The author's script, which previously worked for other races, failed to process the Chong Li GPX files correctly, resulting in overestimated distances and elevation gains. The root cause was identified as the incorrect ordering of track points in the GPX file, which were not sorted by time. The article details the troubleshooting process, the fix, and provides recommendations for race organizers to create cleaner and more compatible GPX files.

## Sanitized Content

Chong Li 168 is a landmark trail race in China: https://www.chongli-ultra.com/ . I went to this years 47K race (TTC) with a group of friends last week.

Someone may know that I have made a script to make time tables based GPX files and check point designations. One example is the Lantau Trail forward 13.5 hours playbook. The script worked pretty well for all races in Hong Kong and almost all good for UTNH (with some slight disturbance).

However, when I applied my script on the GPX files given by organiser of Chong Li series, none worked. The total distance and elevation gain calculated by my script is much larger than that listed on official site. One friend managed to find a watch recorded GPX file of TTC, so we went on with this file. I tried to apply the well known coordinate fix for CN based geo system (Python lib coord-covnert) on the files from organiser but the gap is too large to regard as GPS drift.

On the flight back to Hong Kong, I resumed my troubleshooting.

## Troubleshooting

The first thing to test is to plot the TTC GPX from organiser versus the GPX recorded by a friend.

![TTC compare GPX recorded vs official.png](https://img.hupili.net/images/TTC%20compare%20GPX%20recorded%20vs%20official.png)

The left (blue) is recorded file. The right (red) is the file given by organiser.

It became obvious now that extra distance/ elevation was caused by those jumping lines. Those lines rarely appear on a recorded GPX because even if there are some drift, the magnitude is too small to be visible on this resolution. However, if the GPX file is edited somehow, the sequence of points may not be correct.

I reviewed my script and found out that I **sorted the points by time** (rationale later).

Counting of number of points on each date, we get the following statistics:

```
2022-11-24 3764
2023-06-09 11
2023-06-15 141
9999-12-15 417
```

The "9999-12-15" here is a notation for none date or invalid date. This confirms my conjecture that the course was editted a few times. If we follow the exact order of `time` to transverse the course, we may jump between very remote points.

The fix for me is simple: Use order of points as they appear in the GPX files, instead of sorting by time.

## Sense check

Here's the screenshot of race statistics from official website:

![ChongLi series 2023.jpg](https://img.hupili.net/images/ChongLi%20series%202023.jpg)

Following are the key stats extracted from GPX files after applying my fix above: (The numbers from above table is put side by side after `#` sign).

```
CTC
 'max_elevation': 2128.94921875,
 'min_elevation': 1258.09375,
 'total_ascent': 6120.69140625, #6365
 'total_descent': 6520.015625, #6708
 'total_distance': 131262.781492095,
 'total_distance_in_km': 131.262781492095, #130.6

DTC
 'max_elevation': 2116.80078125,
 'min_elevation': 1235.02734375,
 'total_ascent': 5124.55078125, #4993
 'total_descent': 5125.38671875, #4993
 'total_distance': 98923.20201850265,
 'total_distance_in_km': 98.92320201850265, #99

ETC
 'max_elevation': 2104.94140625,
 'min_elevation': 1258.09375,
 'total_ascent': 1330.890625, #1193
 'total_descent': 1790.9765625, #1542
 'total_distance': 32016.977245265618,
 'total_distance_in_km': 32.016977245265615, # 34.5

GTC
 'max_elevation': 2128.94921875,
 'min_elevation': 790.0,
 'total_ascent': 10091.85546875, #10377
 'total_descent': 9628.34765625, #9923
 'total_distance': 205315.6611457441, #206.2
 'total_distance_in_km': 205.3156611457441,

MTC
 'max_elevation': 2116.80078125,
 'min_elevation': 1252.86328125,
 'total_ascent': 3569.84375, #3608
 'total_descent': 3967.21875, #3935
 'total_distance': 72253.75817713184,
 'total_distance_in_km': 72.25375817713184, #73.9

TTC
 'max_elevation': 2116.80078125,
 'min_elevation': 1252.86328125,
 'total_ascent': 2138.28125, #2190
 'total_descent': 2525.140625, #2529
 'total_distance': 47065.71628622614,
 'total_distance_in_km': 47.06571628622614, #47

UTC
 'max_elevation': 2128.94921875,
 'min_elevation': 1235.02734375,
 'total_ascent': 8235.34375, #8636
 'total_descent': 8236.1796875, #8636
 'total_distance': 170692.42749022238,
 'total_distance_in_km': 170.69242749022237, #169.9
```

We can see that the numbers are very close to the official charts now. TTC and MTC are extremely close in terms of distance and elevation gain. For other races, the elevation gain and loss calculated by my script are both smaller than that announced by organiser. One possible reason is that I applied a 100m smooth distance when calculating elevation gain, in order to reduce GPS drifting issues.

My watch recorded 47.780 KM distance and 2188m elevation gain from TTC. This reconciles with both organiser's number and the one calculated by script.

In general, cumulative GPS drifting is larger when the activity is tracked over longer time / with more rest time/ when the runner is slower. At the same time smooth distance impacts more on the courses that have more frequent fluctuations. In my experience, 100m smooth distance worked well with major races in Hong Kong.

## Rationale of sorting

I started working on GPX files for performance analysis and visualisation purose. Many key metrics are time dependent, e.g. heart rate / lap pace/ etc. Sometimes, I also need to plot part of the course, so using start time & end time is a quick reference of the course segment.

Here's one example of RunArt image one can generate from Strava directly.

![round-lantau-small-loop.png](https://img.hupili.net/images/round-lantau-small-loop.png)

Sorting the GPS points by time made total sense in my initial application. When I applied the planner tool in previous races, there were no frictions, as most established races do not change much of the course. Or, in UTNH's case, the race is too mainstream that someone spent a delibrate effort to record the entire course by watch before the race.

I did not count the possibility of GPX editing in previous versions. Although my script is fixed now, it will be nice for organiser to also clean/ polish their GPX files to be compatible in more scenarios.

## Other issues

Except for those "jumping lines", there are other nit issues of the GPX files. Although they do not impact much of our race planning tool, it is a good practice to further polish the exported file.

Example: track points that include non-necessary data like heart rate and temperature.

```
 <trkpt lat="40.963145177811384" lon="115.27732559479773">
 <ele>1282.3203125</ele>
 <time>2023-06-15T11:13:56Z</time>
 <extensions>
 <gpxtpx:TrackPointExtension>
 <gpxtpx:atemp>33</gpxtpx:atemp>
 <gpxtpx:hr>111</gpxtpx:hr>
 <gpxtpx:cad>0</gpxtpx:cad>
 </gpxtpx:TrackPointExtension>
 <gpxx:TrackPointExtension>
 <gpxx:Temperature>33</gpxx:Temperature>
 </gpxx:TrackPointExtension>
 </extensions>
 </trkpt>
```

Example: track points that do not have `time` attribute at all.

```
 <trkpt lat="40.873035863041878" lon="115.41987050324678">
 <ele>1965.12109375</ele>
 </trkpt>
 <trkpt lat="40.873024296015501" lon="115.41973630897701">
 <ele>1964.6796875</ele>
 </trkpt>
 <trkpt lat="40.873012980446219" lon="115.41960622183979">
 <ele>1963.75</ele>
 </trkpt>
```

Example: waypoints listed in the file do not follow the order that they appear on the course.

```
 <wpt lat="40.859618531540036" lon="115.36391258239746">
 <time>2022-11-22T02:29:20Z</time>
 <name>CP-东坪村</name>
...
<name>CP-二道营</name>
...
<name>CP-转枝莲</name>
...
<name>TTC起点-太舞滑雪小镇</name>
...
<name>起终点-庆典广场</name>
```

## Recommendations

Although I added extra features to my own scripts to handle editted GPX files (assuming the point sequence in file is in order), recommend race organiser to polish their GPX files as follows:

*   Change the time of all GPX points to mockup values so that the list of points sorted by time follows exact order as if the track was recorded by a sport watch.
*   Unify the time to standard presentations (especially when the points come from different sources), e.g. `2023-06-15T11:13:56Z`.
*   Remove non geographic related attributes like heart rate / cadence/ temperature.
*   Sort the CPs (`wpt` in GPX) in order of transverse. Give different names of the CPs if they are transversed multiple times, e.g. "Start - The Square", ... "CP2 - The Square".

### Mockup time script

Here is a quick script to add mockup time to a GPX file.

'''python
'''
Usage:
 gpx_mockup_time.py <input_gpx> <output_gpx>

Options:
 -h help
 -v version
'''

import utils
import docopt
import logging
import math
import numpy as np
import os
import gpxpy 
import gpxpy.gpx
from gpxpy import geo, gpxfield
from datetime import timedelta
from dateutil import parser as dt_parser


def mockup_time(reverse=False):
 if not hasattr(mockup_time, '_last_mockup_time'):
 mockup_time._last_mockup_time = dt_parser.parse('9999-12-15 0:0:1 +08:00')
 if reverse:
 mockup_time._last_mockup_time -= timedelta(seconds=1)
 else:
 mockup_time._last_mockup_time += timedelta(seconds=1)
 return mockup_time._last_mockup_time

if __name__ == "__main__":
 logging.getLogger().setLevel(logging.INFO)
 arguments = docopt.docopt(__doc__)
 gpx_file = open(arguments['<input_gpx>'], 'r') 
 gpx = gpxpy.parse(gpx_file)
 print('Finished loading GPX')
 print(gpx)
 print('Processing mockup time.')
 for track in gpx.tracks:
 for segment in track.segments:
 for point in segment.points:
 point.time = mockup_time()
 c = open(arguments['<output_gpx>'], 'w').write(gpx.to_xml())
 print(f'Write {c} chars to new GPX {arguments["<output_gpx>"]}')
'''
