# Intel Black Light Utility

Written in python, allows you to control the screen brightness (iX processors family), via command line interface.

## Installation

### Arch linux

For archlinux users there's an [AUR package](https://aur.archlinux.org/packages/iblu-git/ "iblu's AUR page").

### Other

Download the script
`$ git clone https://git.eigenlab.org/sbiego/iblu`

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

# NOT mandatory (unless you want to use iblu before rebooting)
$ sudo systemctl start iblu.service
```


##
