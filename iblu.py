#!/usr/bin/python

import sys, math, re
# import getpass
version = "0.5b"

actual_bl = open('/sys/class/backlight/intel_backlight/brightness', 'r+')
actual_brightness = int(actual_bl.read())
max_bl = open('/sys/class/backlight/intel_backlight/max_brightness', 'r')
max_brightness = int(max_bl.read())

help = "Intel Black Light Util · v" + version + "\n\nPlease insert a valid percentage or use inc/dec (i/d) options (optionally indicating the shift)\nExample: \"ibl d 20\" #decreases the blacklight of 20%, default is 4%"
unit = "[Unit]\nDescription=Intel BackLight Util, changes owner of /sys/class/blacklight/intel_blacklight/brightness\n\n[Service]\nExecStart=/usr/bin/chown jake:wheel /sys/class/backlight/intel_backlight/brightness\n\n[Install]\nWantedBy=multi-user.target\n"
argvs = len(sys.argv)
act_info = ''
verbose = 0
changed = 0
shift_percent = math.ceil(max_brightness/100)
percentize = 100/max_brightness
new_brightness = actual_brightness

## todo create function update info for polite coding, there are too many duplicates

if(argvs == 2):
    # option = sys.argv[1]
    if (re.search(r"[v]+", sys.argv[1])):                ##verbose
        verbose = 1
        act_percent = int(actual_brightness * percentize)
        act_info = str(act_percent) + '% (' + str(actual_brightness) + '/' + str(max_brightness) + ')'

    if(re.search(r"[d]|[dec]", sys.argv[1])):
        tmp = actual_brightness - 4 * shift_percent
        new_brightness = max(1, tmp)
        new_percent = int(new_brightness * percentize)
        new_info = str(new_percent) + '% (' + str(new_brightness) + '/' + str(max_brightness) + ')'
        changed = 1
    elif(re.search(r"[i]|[inc]", sys.argv[1])):
        tmp = actual_brightness + 4 * shift_percent
        new_brightness = min(max_brightness, tmp)
        new_percent = int(new_brightness * percentize)
        new_info = str(new_percent) + '% (' + str(new_brightness) + '/' + str(max_brightness) + ')'
        changed = 1
    else:
        if(re.search(r"[0-9]+", sys.argv[1])):
            perc = int(re.findall(r"[0-9]+", sys.argv[1])[0])

            if(perc <= 0):
                new_brightness = 1
            elif(perc < 100):
                new_brightness = min(perc * shift_percent, max_brightness)
            elif(perc >= 100):
                new_brightness = max_brightness

            if not (new_brightness == actual_brightness):
                new_percent = int(new_brightness * percentize)
                new_info = str(new_percent) + '% (' + str(new_brightness) + '/' + str(max_brightness) + ')'
                changed = 1

elif(argvs == 3):
    option = sys.argv[1]
    #re.search(r"d", sys.argv[1])[0]                    ###### TO DO implement regex for custom shift?
    #re.search(r"d", sys.argv[1])[0])
    if(option == 'dec' or option == 'd'):
        new_brightness = max(1, actual_brightness - int(sys.argv[2]) * shift_percent)
        new_percent = int(new_brightness * percentize)
        new_info = str(new_percent) + '% (' + str(new_brightness) + '/' + str(max_brightness) + ')'
        changed = 1
    elif(option == 'inc' or option == 'i'):
        new_brightness = min(max_brightness, actual_brightness + int(sys.argv[2]) * shift_percent)
        new_percent = int(new_brightness * percentize)
        new_info = str(new_percent) + '% (' + str(new_brightness) + '/' + str(max_brightness) + ')'
        changed = 1
else:
    print(help)

if verbose:
    if changed:
        print("old: ", act_info)
        print("new: ", new_info)
    else:
        print("actual: ", act_info)


actual_bl.write(str(new_brightness))
actual_bl.close()


# def output(verbose, perc):
#     if verbose:
#         act_percent = int(actual_brightness * percentize)
#         act_info = "actual: " + str(act_percent) + '% (' + str(actual_brightness) + '/' + str(max_brightness) + ')'
#
#         if perc:
#             new_percent = int(new_brightness * percentize)
#             act_info += "new: " + str(act_percent) + '%'
#
#     print(act_info)
#
# output(verb, perc)
