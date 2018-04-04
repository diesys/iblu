#!/usr/bin/python

import sys, re
# import getpass                        #useful for unit systemd
version = "0.6a"

actual_bl = open('/sys/class/backlight/intel_backlight/brightness', 'r+')
max_bl = open('/sys/class/backlight/intel_backlight/max_brightness', 'r')
state = {'actual': int(actual_bl.read()), 'max': int(max_bl.read()), 'verbose': False, 'changed': False, 'actual_info': '', 'invalid_option': True}
state['new'] = state['actual']
percentize = 100/state['max']
state['actual_pc'] = int(state['actual'] * percentize)

state['actual_info'] = str(int(state['actual'] * percentize)) + '% (' + str(state['actual']) + '/' + str(state['max']) + ')'
shift_one_pc = int(state['max']/100)                    #unita' percentuale sulla luminosita' massima
shift_std_pc = 4                                      #unita' standard di aumento/decremento in percentuale
shift_factor = shift_std_pc * shift_one_pc              #fattore moltiplicativo non in percentuale
argvs = len(sys.argv)

help = "Intel Black Light Util · v" + version + "\n\n\t0-100\t\tsets to the given percentage\n\ti (inc)\t\tincreases the actual backlight\n\td (dec)\t\tdecreases the actual backlight\n\ta (act)\t\tshows the actual\n\tv\t\tshows verbose output\n"

unit = "[Unit]\nDescription=Intel BackLight Util, changes owner of /sys/class/blacklight/intel_blacklight/brightness\n\n[Service]\nExecStart=/usr/bin/chown jake:wheel /sys/class/backlight/intel_backlight/brightness\n\n[Install]\nWantedBy=multi-user.target\n"

#### todo
### percentuale sbagliata
### FARE UNA REGEX ALL'INIZIO E POI LE SOTTOSELEZIONI CON LE PIU SEMPLICI
# === futuro
# = option for creating unit and enabling/disabling
# = capability to create keybindings, tty use or something not working with the DE

def updateState(new_brightness):
    new_brightness = int(new_brightness)
    if(new_brightness != state['actual_pc']):
        if(new_brightness <= 0):
            state['new'] = 1
        elif(new_brightness < 100):
            state['new'] = min(new_brightness * shift_one_pc, state['max'])
        elif(new_brightness == 100):
            state['new'] = state['max']
    
        state['changed'] = True
    
    else:
        state['changed'] = False

    state['new'] = int(new_brightness)
    state['new_pc'] = int(state['new'] * percentize)
    state['new_info'] = str(state['new_pc']) + '% (' + str(state['new']) + '/' + str(state['max']) + ')'
    state['invalid_option'] = False
    
    verboseOut()        ## debug

def verboseOut():
    if state['changed']:
        print("old: ", state['actual_info'])
        print("new: ", state['new_info'])
    else:
        print("actual: ", state['actual_info'])
 
def decrease(percentage=shift_std_pc):
    updateState(int(state['actual'] - shift_one_pc * percentage))
    print(int(state['actual'] - shift_one_pc * percentage))

def increase(percentage=shift_std_pc):
    updateState(int(state['actual'] + shift_one_pc * percentage))
    print(int(state['actual'] + shift_one_pc * percentage))


###
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