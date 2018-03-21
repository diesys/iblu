#!/usr/bin/python

import sys, math, getpass
version = "0.4b"

actual_bl = open('/sys/class/backlight/intel_backlight/brightness','r+')
actual_brightness = int(actual_bl.read())
max_bl = open('/sys/class/backlight/intel_backlight/max_brightness','r')
max_brightness = int(max_bl.read())

help = "Intel Black Light Util · v" + version + "\n\nPlease insert a valid percentage or use inc/dec (i/d) options (optionally indicating the shift)\nExample: \"ibl d 20\" #decreases the blacklight of 20%, default is 5%"
unit = "[Unit]\nDescription=Intel BackLight Util, changes owner of /sys/class/blacklight/intel_blacklight/brightness\n\n[Service]\nExecStart=/usr/bin/chown jake:wheel /sys/class/backlight/intel_backlight/brightness\n\n[Install]\nWantedBy=multi-user.target\n"
argvs = len(sys.argv)
shift_percent = math.ceil(max_brightness/100)
new_brightness = actual_brightness

if(argvs == 2):
    option = sys.argv[1]
    if(option == 'dec' or option == 'd'):
        tmp = actual_brightness - 5 * shift_percent
        new_brightness = max(1, tmp)
    elif(option == 'inc' or option == 'i'):
        tmp = actual_brightness + 5 * shift_percent
        new_brightness = min(max_brightness, tmp)
    else:
        perc = int(sys.argv[1])
        if(perc <= 0):
            new_brightness = 1
        elif(perc <= 100):
            new_brightness = perc * shift_percent
        elif(perc > 100):
            new_brightness = max_brightness
elif(argvs == 3):
    option = sys.argv[1]
    if(option == 'dec' or option == 'd'):
        new_brightness = max(1, actual_brightness - int(sys.argv[2]) * shift_percent)
    elif(option == 'inc' or option == 'i'):
        new_brightness = min(max_brightness, actual_brightness + int(sys.argv[2]) * shift_percent)
else:
    print(help)

#     username = getpass.getuser()
#     if(sys.argv[1] == 'enable'):
#          if(not os.path.exists('/etc/systemd/system/iblu.service')):
#              unit_file = open('/etc/systemd/system/iblu.service', 'w')
#              # unit_file.write(unit)
#              print(unit)
    # if(sys.argv[1] == 'disable'):

actual_bl.write(str(new_brightness))
actual_bl.close()
