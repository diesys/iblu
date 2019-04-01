# Intel Black Light Utility

![iblu_logo](https://git.eigenlab.org/uploads/-/system/project/avatar/75/iblu_logo.png?width=52)

Written in python, allows you to control the screen brightness (iX processors family), via command line interface.

## Installation

### Arch linux

For archlinux users there's an [AUR package](https://aur.archlinux.org/packages/iblu-git/ "iblu's AUR page").

### Other

Download the script
```sh
$ git clone https://git.eigenlab.org/sbiego/iblu
```

Make it executable and copy it /usr/bin

```sh
$ chmod +x iblu/iblu.py
$ sudo cp iblu/iblu.py /usr/bin/iblu
```

Create the unit file (permissions of the brightness file in '/sys/')

```sh
# create unit file
$ iblu UNIT > /usr/lib/systemd/system/iblu.service

# autorun at BOOT
$ sudo systemctl enable iblu.service
```
Done!

If you dont want to reboot to use iblu start the service right now:

```sh
$ sudo systemctl start iblu.service
```


## Usage

  * **0-100**		sets backlight to the given percentage
  * **i (inc)**		increases backlight by a step, optionally add a number to custom percentage (default is 3%)
  * **d (dec)**		decreases backlight, optionally add a number to custom percentage (default is 3%)
  * **c (curr)**		shows the current
  * **v**		shows verbose output
  * **V**		shows very verbose output (for debug)
  * **OFF**		turns off backlight (use with a grain of salt)
  * **UNIT**	prompts in terminal the Systemd unit raw text (better using with I/O redirecting)

### Examples
```sh
iblu i30	#increases of 30% the current backlight (30 is optional)
```
