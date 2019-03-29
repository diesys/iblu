#!/bin/bash

currentBL=$( cat /sys/class/backlight/intel_backlight/brightness )
brightnessFILE='/sys/class/backlight/intel_backlight/brightness'
delta=100

if [[ $1 == "-i" ]]
	then
		# echo $(( $( cat /sys/class/backlight/intel_backlight/brightness) + 100 )) #> /sys/class/backlight/intel_backlight/brightness
		echo $(( $currentBL + 100 )) #> /sys/class/backlight/intel_backlight/brightness

elif [[ $1 == "-d" ]]
	then
		if [[ $(( $(( $currentBL - $delta )) > 0 )) ]]
			then
				# echo $(( $( cat /sys/class/backlight/intel_backlight/brightness) - 100 )) #> /sys/class/backlight/intel_backlight/brightness
				echo $(( $currentBL - $delta )) #> /sys/class/backlight/intel_backlight/brightness
		fi

else
	if [[ $(( $(( $1 )) > 101 )) && $(( $(( $1 )) < 0 )) ]]
		then
			echo $(( (851*$1/100)+1 )) #> /sys/class/backlight/intel_backlight/brightness

	else
		echo -e "·· Intel BackLight Util ··\n\t-d\t dims backlight a bit\n\t-i\t increases backlight a bit\n\t0..100\t sets a precise percentage (0 is not off)\n"

	fi

fi
