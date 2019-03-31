#!/usr/bin/python

import sys, re, math, getpass
# import getpass                        #useful for unit systemd
version = "0.8"

current_bl = open('/sys/class/backlight/intel_backlight/brightness', 'r+')
max_bl = open('/sys/class/backlight/intel_backlight/max_brightness', 'r')
state = {'current': int(current_bl.read()), 'max': int(max_bl.read()), 'changed': False, 'current_info': '', 'invalid_option': True}
state['new'] = state['current']
percentize = 100/state['max']
shift_one_pc = int(state['max'])/100                    #unita' percentuale sulla luminosita' massima
shift_std_pc = 3                                      #unita' standard di aumento/decremento in percentuale
shift_factor = shift_std_pc * shift_one_pc              #fattore moltiplicativo non in percentuale
state['current_pc'] = 0 if (state['current'] < shift_one_pc-1) else math.ceil(int(state['current']) * percentize)

state['current_info'] = str(state['current_pc']) + '% (' + str(state['current']) + '/' + str(state['max']) + ')'

help = "Intel Black Light Util · v" + version + "\n\n\t0-100\t\tsets backlight to the given percentage\n\ti (inc)\t\tincreases backlight by a step, optionally add a number to custom percentage (default is " + str(shift_std_pc) + "%)\n\td (dec)\t\tdecreases backlight, optionally add a number to custom percentage (default is " + str(shift_std_pc) + "%)\n\tc (curr)\t\tshows the current\n\tv\t\tshows verbose output\n\tV\t\tshows very verbose output (for debug)\n\tOFF\t\tturns off backlight (use with a grain of salt)\n\nexample: iblu i30\t#increases of 30% the current backlight (30 is optional)"

unit = "[Unit]\nDescription=Intel BackLight Util, changes owner of /sys/class/blacklight/intel_blacklight/brightness\n\n[Service]\nExecStart=/usr/bin/chown " + getpass.getuser() + ":wheel /sys/class/backlight/intel_backlight/brightness\n\n[Install]\nWantedBy=multi-user.target\n"

#### todo
### FARE UNA REGEX ALL'INIZIO E POI LE SOTTOSELEZIONI CON LE PIU SEMPLICI (utile per parametri giusti e no e semplificare regex)
### migliore verbose mode/debug su OFF
# === futuro
# = option for creating unit and enabling/disabling
# = capability to create keybindings, tty use or something not working with the DE

def updateState(new_percent):
    new_percent = int(new_percent)
    new_brightness = math.floor(new_percent * shift_one_pc)
    if(state['current'] - new_brightness > 1 ):                   ## to prevent approx errors and 0 value errors
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
    state['new_pc'] = 0 if (new_percent < 0) else new_percent
    state['new_info'] = str(state['new_pc']) + '% (' + str(state['new']) + '/' + str(state['max']) + ')'
    state['invalid_option'] = False

def verboseOut(print_state=False):
    if state['changed']:
        print("old: ", state['current_info'])
        print("new: ", state['new_info'])
    else:
        print("current: ", state['current_info'])
 
    if(print_state):
        print(state)
 
def decrease(percentage=shift_std_pc):
    updateState(int(state['current_pc']) - percentage)

def increase(percentage=shift_std_pc):
    updateState(int(state['current_pc']) + percentage)


if(len(sys.argv) == 2):                                              ## getting parameters if exist
    option = sys.argv[1]

    # percentage set
    if(re.search(r"^[v|V]{0,1}[100]{1}$|^[100]{1}[v|V]{0,1}$|^[v|V]{0,1}[0-9]{1,2}$|^[0-9]{1,2}[v|V]{0,1}$", option)):  ## percentage
        input_number = re.findall(r"100|[0-9]{0,2}", option)
        if(input_number[0]):
            updateState(input_number[0])
        elif(input_number[1]):
            updateState(input_number[1])
        if(re.search(r"[v|V]{1}", option)):                                                 ## verbose
            debug = True if(re.search(r"V", option)) else False
            verboseOut(debug)

    # decrease 1
    if(re.search(r"^[v|V]{0,1}d$|^d[v|V]{0,1}$|^[v|V]{0,1}dec$|^dec[v|V]{0,1}$", option)):                                  ## decrease bl by a step
        decrease()
        if(re.search(r"[v|V]{1}", option)):                                                 ## verbose
            debug = True if(re.search(r"V", option)) else False
            verboseOut(debug)

    # 2 decrease
    if(re.search(r"^d[0-9]{1,2}$|^dec[0-9]{1,2}$|^[0-9]{1,2}d$|^[0-9]{1,2}dec$", option)):                               ## dec bl by percentage
        decrease(int(re.findall(r"[0-9]{1,2}", option)[0]))
        if(re.search(r"[v|V]{1}", option)):                                                 ## verbose
            debug = True if(re.search(r"V", option)) else False
            verboseOut(debug)

    # increase 1
    if(re.search(r"^i$|^inc$", option)):                                       ## increase bl by a step
        increase()
        if(re.search(r"[v|V]{1}", option)):                                                 ## verbose
            debug = True if(re.search(r"V", option)) else False
            verboseOut(debug)

    # 2 increase
    if(re.search(r"^i[0-9]{1,2}$|^inc[0-9]{1,2}$|^[0-9]{1,2}i$|^[0-9]{1,2}inc$", option)):                                ## inc bl by percentage
        increase(int(re.findall(r"[0-9]{1,2}", option)[0]))
        if(re.search(r"[v|V]{1}", option)):                                                 ## verbose
            debug = True if(re.search(r"V", option)) else False
            verboseOut(debug)
    
    # current info
    if(re.search(r"^c$|^curr$", option)):                                  ## see current bl
        state['invalid_option'] = False
        debug = True if(re.search(r"V", option)) else False
        verboseOut(debug)
    
    # turns off
    if(re.search(r"^OFF$", option)):                                  
        state['invalid_option'] = False
        state['new'] = 0
        debug = True if(re.search(r"V", option)) else False
        verboseOut(debug)
    
    # install unit systemd file
    if(re.search(r"^--install$", option)):                                  
        state['invalid_option'] = False
        print(unit) 
        # debug = True if(re.search(r"V", option)) else False
        # verboseOut(debug)

if(state['invalid_option']):
    print(help)


#verboseOut(True)        ## debug
current_bl.write(str(state['new']))
current_bl.close()