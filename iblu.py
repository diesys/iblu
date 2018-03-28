#!/usr/bin/python

import sys, re
# import getpass                        #useful for unit systemd
version = "0.5e"

actual_bl = open('/sys/class/backlight/intel_backlight/brightness', 'r+')
max_bl = open('/sys/class/backlight/intel_backlight/max_brightness', 'r')
state = {'actual': int(actual_bl.read()), 'max': int(max_bl.read()), 'verbose': False, 'changed': False, 'actual_info': ''}
percentize = 100/state['max']
state['new'] = state['actual']
state['actual_info'] = str(int(state['actual'] * percentize)) + '% (' + str(state['actual']) + '/' + str(state['max']) + ')'
shift_one_pc = int(state['max']/100)                    #unita' percentuale sulla luminosita' massima
shift_std_pc = 4                                        #unita' standard di aumento/decremento in percentuale
shift_factor = shift_std_pc * shift_one_pc              #fattore moltiplicativo non in percentuale
argvs = len(sys.argv)

help = "Intel Black Light Util · v" + version + "\nPlease insert a valid percentage or use inc/dec (i/d) options (optionally indicating the shift)\nExample: \"ibl d 20\" #decreases the blacklight of 20%, default is 4%"
unit = "[Unit]\nDescription=Intel BackLight Util, changes owner of /sys/class/blacklight/intel_blacklight/brightness\n\n[Service]\nExecStart=/usr/bin/chown jake:wheel /sys/class/backlight/intel_backlight/brightness\n\n[Install]\nWantedBy=multi-user.target\n"

#### todo
# rifare help
# option for creating unit and enabling/disabling
# capability to create keybindings, tty use or something not working with the DE

def update_state(actual_brightness, new_brightness):
    state['actual'] = int(actual_brightness)
    state['actual_pc'] = int(state['actual'] * percentize)
    state['new'] = int(new_brightness)
    state['new_pc'] = int(state['new'] * percentize)
    state['new_info'] = str(state['new_pc']) + '% (' + str(state['new']) + '/' + str(state['max']) + ')'
    state['changed'] = True

if(argvs == 2):
    option = sys.argv[1]
    if(re.search(r"[v]+", option)):                ##verbose
        state['verbose'] = True
        state['actual_pc'] = int(state['actual'] * percentize)

    if(re.search(r"[d]|[dec]", option)):
        tmp = state['actual'] - shift_factor
        state['new'] = max(1, tmp)
        update_state(int(state['actual']), int(state['new']))
    elif(re.search(r"[i]|[inc]", option)):
        tmp = state['actual'] + shift_factor
        state['new'] = min(state['max'], tmp)
        update_state(int(state['actual']), int(state['new']))
    else:
        if(re.search(r"[0-9]+", option)):
            perc = int(re.findall(r"[0-9]+", option)[0])

            if(perc <= 0):
                state['new'] = 1
            elif(perc < 100):
                state['new'] = min(perc * shift_one_pc, state['max'])
            elif(perc == 100):
                state['new'] = state['max']
            else:
                print(help)

            if not (state['new'] == state['actual']):
                update_state(state['actual'], int(state['new']))

elif(argvs == 3):
    option = sys.argv[1]
    increment_pc = int(sys.argv[2]) * shift_one_pc
    if(option == 'dec' or option == 'd'):
        state['new'] = max(1, state['actual'] - increment_pc)
        update_state(int(state['actual']), int(state['new']))
    elif(option == 'inc' or option == 'i'):
        state['new'] = min(state['max'], state['actual'] + increment_pc)
        update_state(int(state['actual']), int(state['new']))
else:
    print(help)

if state['verbose']:
    if state['changed']:
        print("old: ", state['actual_info'])
        print("new: ", state['new_info'])
    else:
        print("actual: ", state['actual_info'])

actual_bl.write(str(state['new']))
actual_bl.close()
