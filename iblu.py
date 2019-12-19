#!/usr/bin/env python3

import sys, re, math, getpass
from os import chdir
from subprocess import run, PIPE
from pathlib import Path

# import getpass                        #useful for unit systemd
# version = "0.9"

current_bl = open('/sys/class/backlight/intel_backlight/brightness', 'r+')
max_bl = open('/sys/class/backlight/intel_backlight/max_brightness', 'r')
state = {'version': "0.9", 'current': int(current_bl.read()), 'max': int(max_bl.read()), 'changed': False, 'current_info': '', 'invalid_option': True,\
        'executable': Path('/usr/bin/iblu'), 'src_dir': Path('/usr/share/iblu'),\
        'git_repo': 'https://git.eigenlab.org/sbiego/iblu.git'}
state['new'] = state['current']
percentize = 100/state['max']
shift_one_pc = int(state['max'])/100                    #unita' percentuale sulla luminosita' massima
shift_std_pc = 3                                        #unita' standard di aumento/decremento in percentuale
shift_factor = shift_std_pc * shift_one_pc              #fattore moltiplicativo non in percentuale
state['current_pc'] = 0 if (state['current'] < shift_one_pc-1) else math.ceil(int(state['current']) * percentize)

state['current_info'] = str(state['current_pc']) + '% (' + str(state['current']) + '/' + str(state['max']) + ')'

unit = "[Unit]\nDescription=Intel BackLight Util, changes owner of /sys/class/blacklight/intel_blacklight/brightness\n\n[Service]\nExecStart=/usr/bin/chown " + getpass.getuser() + ":wheel /sys/class/backlight/intel_backlight/brightness\n\n[Install]\nWantedBy=multi-user.target\n"

## IMPORTED FROM MOTOGIF
HELP = {"asciiart": "   _ __   __\n  (_) / / / _ __\n / / _ \/ / // /\n/_/_.__/_/\_,_/ v",
        "title": "iblu",
        "version": "",
        "descr": "\nIntel Black-Light Util: a simple utility to change backlight via cli.\n",
        "usage": "\n\t0-100\t\tsets backlight to the given percentage\n\ti (inc)\t\tincreases backlight by a step, optionally add a number to custom percentage (default is " + str(shift_std_pc) + "%)\n\td (dec)\t\tdecreases backlight, optionally add a number to custom percentage (default is " + str(shift_std_pc) + "%)\n\tc (curr)\t\tshows the current\n\tv\t\tshows verbose output\n\tV\t\tshows very verbose output (for debug)\n\tOFF\t\tturns off backlight (use with a grain of salt)\n\tUNIT\t\tprompts in terminal the Systemd unit raw text (better using with I/O redirecting)\n\n\t--install \tinstall from local directory (a cloned repo!)\n\t--install-git\tclone the online repo and install it into the system\n\t-u, --update\tchek for any new commits from git repo and install them\n\nexample: iblu i30\t#increases of 30% the current backlight (30 is optional)\n",
        # "notes": "\n\n\t! WARNING: motogif may overwrite or remove its own temp files or any files passed as argument",
        "license": "\nLICENSE: GPLv3 - https://www.gnu.org/licenses/gpl-3.0.html\n",
        "repo": "\nGit repo: 'https://git.eigenlab.org/sbiego/iblu.git'",
        "sysd_unit" : "[Unit]\nDescription=Intel BackLight Util, changes owner of /sys/class/blacklight/intel_blacklight/brightness\n\n[Service]\nExecStart=/usr/bin/chown " + getpass.getuser() + ":wheel /sys/class/backlight/intel_backlight/brightness\n\n[Install]\nWantedBy=multi-user.target\n"
        }

def calcRevision():
	if state['src_dir'].exists() and re.search('^[0-9]+.[0-9]+$', state['version']):
		cwd = Path.cwd()
		chdir(state['src_dir'])
		update_version = ''
		if Path('.git').exists():
			# using git number of commit, adding revision to the major version
			git_log = run(['git', 'log', '--oneline'], stdout=PIPE,
			              stderr=PIPE, universal_newlines=True)
			# the new command to be compiled (down)
			update_version = "state['version']=str('" + str(
				state['version']) + "'+'-'+'" + str(len(re.findall('\n', git_log.stdout))) + "');"
			# write it in the HELP too
			update_version += "HELP['version']+=state['version']"
			chdir(cwd)

		# the new command being compiled and evaluated, so the revision is added to the major version (A.BC-XY)
		newcode = compile(update_version, "", 'exec')
		eval(newcode)


def promptHelp(info, sections=['asciiart', 'version', 'descr', 'usage']):
	help = ''
	for section in sections:
		help += HELP[section]
		# print(HELP[section])
	if info != '':
		help += str('\n\n· ' + info + '\n')
		# print('· ' + info)
	print(help)
	exit


def install(opt='local'):
	print("· Cloning into "+ str(state['src_dir']) +" ...")
	if not state['src_dir'].exists():
		print("· Creating the folder ...")
		run(['sudo', 'mkdir', state['src_dir']])

	if opt == 'git':
		git_clone = run(['git', 'clone', str(state['git_repo']), '/tmp/iblu', '--progress'], stdout=PIPE, stderr=PIPE, universal_newlines=True)
		print(git_clone.stdout)
		run(['sudo', 'cp', '-r', '/tmp/iblu', str(state['src_dir'])])
	elif opt == 'local':
		run(['sudo', 'cp', '-r', '.', str(state['src_dir'])])

	print("· Linking the executable " + str(state['executable']) + " ...")
	run(['sudo', 'ln', '-fs', Path(str(state['src_dir'])+'/iblu.py'), state['executable']], stdout=PIPE, stderr=PIPE, universal_newlines=True)
	print('Done')
	promptHelp('', ['usage'])
	exit

def update():
	cwd = Path.cwd()
	chdir(state['src_dir'])
	git_pull=run(['sudo', 'git', 'pull', state['git_repo'], '--progress'], stdout=PIPE, stderr=PIPE, universal_newlines=True)
	chdir(cwd)
	print(git_pull.stdout)

### TODO
#   - usare +/- non i e d..........
#   - attivare/disattivare/controllare stato direttamente della unit systemd da iblu
# ····························
### FARE UNA REGEX ALL'INIZIO E POI LE SOTTOSELEZIONI CON LE PIU SEMPLICI (utile per parametri giusti e no e semplificare regex)
### migliore verbose mode/debug su OFF
# ··········· futuro
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
    else:
        state['changed'] = False

    state['new'] = max(int(new_brightness), 1)             ## to prevent blank screen
    state['new_pc'] = 0 if (new_percent < 0) else new_percent
    state['new_info'] = str(state['new_pc']) + '% (' + str(state['new']) + '/' + str(state['max']) + ')'
    state['invalid_option'] = False
    state['changed'] = True

def verboseOut(print_state=False):
    if state['changed']:
        # print("old: ", state['current_info'])
        print("new: ", state['new_info'])
    else:
        print("current: ", state['current_info'])
 
    if(print_state):
        print(state)
 
def decrease(percentage=shift_std_pc):
    updateState(int(state['current_pc']) - percentage)

def increase(percentage=shift_std_pc):
    updateState(int(state['current_pc']) + percentage)


calcRevision()
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
    elif(re.search(r"^[v|V]{0,1}d$|^d[v|V]{0,1}$|^[v|V]{0,1}dec$|^dec[v|V]{0,1}$", option)):                                  ## decrease bl by a step
        decrease()
        if(re.search(r"[v|V]{1}", option)):                                                 ## verbose
            debug = True if(re.search(r"V", option)) else False
            verboseOut(debug)

    # 2 decrease
    elif(re.search(r"^d[0-9]{1,2}$|^dec[0-9]{1,2}$|^[0-9]{1,2}d$|^[0-9]{1,2}dec$", option)):                               ## dec bl by percentage
        decrease(int(re.findall(r"[0-9]{1,2}", option)[0]))
        if(re.search(r"[v|V]{1}", option)):                                                 ## verbose
            debug = True if(re.search(r"V", option)) else False
            verboseOut(debug)

    # increase 1
    elif(re.search(r"^i$|^inc$", option)):                                       ## increase bl by a step
        increase()
        if(re.search(r"[v|V]{1}", option)):                                                 ## verbose
            debug = True if(re.search(r"V", option)) else False
            verboseOut(debug)

    # 2 increase
    elif(re.search(r"^i[0-9]{1,2}$|^inc[0-9]{1,2}$|^[0-9]{1,2}i$|^[0-9]{1,2}inc$", option)):                                ## inc bl by percentage
        increase(int(re.findall(r"[0-9]{1,2}", option)[0]))
        if(re.search(r"[v|V]{1}", option)):                                                 ## verbose
            debug = True if(re.search(r"V", option)) else False
            verboseOut(debug)
    
    # current info
    elif(re.search(r"^c$|^curr$", option)):                                  ## see current bl
        debug = True if(re.search(r"V", option)) else False
        verboseOut(debug)
    
    # install
    elif(re.search(r"^--install(-git)*$", option)):                                  
        promptHelp('Installing ...', ['asciiart', 'version'])
        if len(sys.argv) == 3 and re.search("^git$", sys.argv[2]):
            install('git')
            exit
        else:
            install()
            exit
        debug = True if(re.search(r"V", option)) else False
        verboseOut(debug)

    # update
    elif re.search("^-+(-update|u)$", sys.argv[1]):
        promptHelp('Updating ...', ['asciiart', 'version'])
        update()
    
    # version
    elif re.search("^--version$", sys.argv[1]):
        print(state['version'])

    # turns off
    elif(re.search(r"^OFF$", option)):                                  
        state['new'] = 0
        debug = True if(re.search(r"V", option)) else False
        verboseOut(debug)
    
    # prints the systemd unit file
    elif(re.search(r"^UNIT$", option)):                                   
        print(unit) 

if len(sys.argv) == 1 or re.search("^-(h|-help)$", sys.argv[1]):
    # print(help)
    promptHelp('')

# writing the file.. actual changing brightness
#verboseOut(True)        ## debug
current_bl.write(str(state['new']))
current_bl.close()
