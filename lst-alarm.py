import os
import sys
import time
import ephem
import numpy as np

# process command line
nargs = len(sys.argv) - 1
if (nargs==1):
    lst_alarm_hms = sys.argv[1]
    lst_alarm_split = lst_alarm_hms.split(":")
    if len(lst_alarm_split)==2:
        lst_alarm = (np.float(lst_alarm_split[0])
                     + np.float(lst_alarm_split[1])/60.0)
    if len(lst_alarm_split)==3:
        lst_alarm = (np.float(lst_alarm_split[0])
                     + np.float(lst_alarm_split[1])/60.0
                     + np.float(lst_alarm_split[2])/3600.0)
    if len(lst_alarm_split)!=2 and len(lst_alarm_split)!=3:
        print("Invalid LST")
        sys.exit()
else:
    print("Needs an LST to set an alarm")
    print("python lst-alarm.py 14:31:15")
    sys.exit()
                
# set up data for Molonglo as an observatory site
# from https://sites.google.com/a/utmostproject.org/internal/telescope-specifics/location
# -35° 22' 14.5452" (-35.370707 deg), 149° 25' 28.7682" (149.424658 deg).
utmost = ephem.Observer()
utmost.lon = '149.424658' # deg
utmost.lat = '-35.370707' # deg
utmost.elevation = 700  # meters, a guess

# what's the GMT/UTC right now based on system clock
nowgmt = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
utmost.date = nowgmt
utmost_lst = str(utmost.sidereal_time())
utmost_lst = utmost_lst.split(":")
utmost_lst = np.float(utmost_lst[0]) + np.float(utmost_lst[1])/60.0 + np.float(utmost_lst[2])/3600.0
utmost_lst = np.around(utmost_lst,3)

# figure out whether we are before or after the LST alarm time on a 0-24 hour scale
toggle = utmost_lst < lst_alarm
toggle_flip = False

# keep looping until a "before/after alarm LST" check changes state
while not toggle_flip:

    # first get the UTC now and figure out LST at the observatory
    nowgmt = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    utmost.date = nowgmt
    utmost_lst_hms = str(utmost.sidereal_time())
    utmost_lst = utmost_lst_hms.split(":")
    utmost_lst = np.float(utmost_lst[0]) + np.float(utmost_lst[1])/60.0 + np.float(utmost_lst[2])/3600.0

    # now check if we have drifted past the set alarm time
    toggle_check = utmost_lst < lst_alarm
    if toggle_check != toggle:
        toggle_flip = True

    # compute the remaining time to go
    remain_time = lst_alarm - utmost_lst
    if remain_time < 0:
        remain_time += 24.0

    # convert remaining time into an HH:MM:SS.S string    
    remain_hrs = np.int(remain_time)
    remain_time = remain_time - remain_hrs
    remain_mins = np.int(remain_time*60.0)
    remain_time = remain_time*60.0 - remain_mins
    remain_secs = remain_time*60.0
    # deal with leading "0"s -- add these if necessary
    if len(str(remain_hrs))==1:
        remain_hrs = "0"+str(remain_hrs)
    if len(str(remain_mins))==1:
        remain_mins = "0"+str(remain_mins)
    remain_secs = np.around(remain_secs,1)
    if len(str(remain_secs).split(".")[0]) == 1:
        remain_secs = "0"+str(remain_secs)
    remain_time_hms = str(remain_hrs)+":"+str(remain_mins)+":"+str(remain_secs)
    
    # print out the clocks and remain time etc
    print("  GMT/UTC : ",nowgmt,
          " | LST : ", utmost_lst_hms,
          " | Alarm LST : ",lst_alarm_hms,
          " | Remaining time : ",remain_time_hms,
          end='\r', flush=True)

    # sleep for 1 second
    time.sleep(1)

print()
    
duration = 1  # seconds
freq = 440  # Hz

print("Your LST has been reached")
for i in range(5):
    os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq))
    time.sleep(0.3)

