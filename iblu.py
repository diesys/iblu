#!/usr/bin/python

import sys, re, math
# import getpass                        #useful for unit systemd
version = "0.6c"

actual_bl = open('/sys/class/backlight/intel_backlight/brightness', 'r+')
max_bl = open('/sys/class/backlight/intel_backlight/max_brightness', 'r')
state = {'actual': int(actual_bl.read()), 'max': int(max_bl.read()), 'changed': False, 'actual_info': '', 'invalid_option': True}
state['new'] = state['actual']
percentize = 100/state['max']
shift_one_pc = int(state['max'])/100                    #unita' percentuale sulla luminosita' massima
shift_std_pc = 4                                      #unita' standard di aumento/decremento in percentuale
shift_factor = shift_std_pc * shift_one_pc              #fattore moltiplicativo non in percentuale
state['actual_pc'] = 0 if (state['actual'] < shift_one_pc-1) else math.ceil(int(state['actual']) * percentize)

state['actual_info'] = str(state['actual_pc']) + '% (' + str(state['actual']) + '/' + str(state['max']) + ')'

help = "Intel Black Light Util · v" + version + "\n\n\t0-100\t\tsets to the given percentage\n\ti (inc)\t\tincreases the actual backlight\n\td (dec)\t\tdecreases the actual backlight\n\ta (act)\t\tshows the actual\n\tv\t\tshows verbose output\n"

unit = "[Unit]\nDescription=Intel BackLight Util, changes owner of /sys/class/blacklight/intel_blacklight/brightness\n\n[Service]\nExecStart=/usr/bin/chown jake:wheel /sys/class/backlight/intel_backlight/brightness\n\n[Install]\nWantedBy=multi-user.target\n"

#### todo
### FARE UNA REGEX ALL'INIZIO E POI LE SOTTOSELEZIONI CON LE PIU SEMPLICI
# === futuro
# = option for creating unit and enabling/disabling
# = capability to create keybindings, tty use or something not working with the DE

def updateState(new_percent):
    new_percent = int(new_percent)
    new_brightness = math.floor(new_percent * shift_one_pc)
    if(state['actual'] - new_brightness > 1):                   ## to prevent approx errors
        print(state['actual'] - new_brightness < 1)
        if(new_percent <= 0):
            new_brightness = 1
        elif(new_percent < 100):
            new_brightness = min(new_percent * shift_one_pc, state['max'])
        elif(new_brightness == 100):
            new_brightness = state['max']
    
        state['changed'] = True
    
    else:
        state['changed'] = False

    state['new'] = max(int(new_brightness), 1)             ## to prevent blank screen
    state['new_pc'] = new_percent
    state['new_info'] = str(state['new_pc']) + '% (' + str(state['new']) + '/' + str(state['max']) + ')'
    state['invalid_option'] = False

def verboseOut(print_state=False):
    if state['changed']:
        print("old: ", state['actual_info'])
        print("new: ", state['new_info'])
    else:
        print("actual: ", state['actual_info'])
 
    if(print_state):
        print(state)
 
def decrease(percentage=shift_std_pc):
    updateState(int(state['actual']) - shift_one_pc * percentage)
    #print(int(state['actual'] - shift_one_pc * percentage))

def increase(percentage=shift_std_pc):
    updateState(int(state['actual']) + shift_one_pc * percentage)
    #print(int(state['actual'] + shift_one_pc * percentage))


if(len(sys.argv) == 2):                                              ## getting parameters if exist
    option = sys.argv[1]

    if(re.search(r"^[v]{0,1}[100]{1}$|^[100]{1}[v]{0,1}$|^[v]{0,1}[0-9]{1,2}$|^[0-9]{1,2}[v]{0,1}$", option)):  ## percentage
        input_number = re.findall(r"100|[0-9]{0,2}", option)
        if(input_number[0]):
            # setPercent(input_number[0])
            updateState(input_number[0])
        elif(input_number[1]):
            # setPercent(input_number[1])
            updateState(input_number[1])
        if(re.search(r"[v]{1}", option)):                                                 ## verbose
            verboseOut()

    if(re.search(r"^[v]{0,1}d$|^d[v]{0,1}$|^[v]{0,1}dec$|^dec[v]{0,1}$", option)):                                  ## decrease bl by a step
        decrease()
        # print(re.findall(r"^d$", option)[0])
        if(re.search(r"[v]{1}", option)):                                                 ## verbose
            verboseOut()

    if(re.search(r"^d[0-9]{1,2}$|^dec[0-9]{1,2}$", option)):                               ## dec bl by percentage
        decrease(int(re.findall(r"[0-9]{1,2}", option)[0]))
        if(re.search(r"[v]{1}", option)):                                                 ## verbose
            verboseOut()

    if(re.search(r"^i$|^inc$", option)):                                       ## increase bl by a step
        increase()
        if(re.search(r"[v]{1}", option)):                                                 ## verbose
            verboseOut()

    if(re.search(r"^i[0-9]{1,2}$|^inc[0-9]{1,2}$", option)):                                ## inc bl by percentage
        increase(int(re.findall(r"[0-9]{1,2}", option)[0]))
        if(re.search(r"[v]{1}", option)):                                                 ## verbose
            verboseOut()
    
    if(re.search(r"^a$|^act$", option)):                                  ## see actual bl
        state['invalid_option'] = False
        verboseOut()

if(state['invalid_option']):
    print(help)

actual_bl.write(str(state['new']))
actual_bl.close()
verboseOut(True)        ## debug