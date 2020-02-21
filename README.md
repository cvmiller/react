## Synopsis


A python game played with just one LED and one Switch (push button) on a Raspberry Pi.

The game measures the reaction time of the player, but lighting the LED, and the player pushing the push button as quickly as they can to turn the LED off. The amount of time is measured, and after 3 rounds (of playing the game), the reaction times are printed (in mili-seconds)


## Motivation

In teaching Introduction to Pi classes, students are taught how to safely connect LEDs and Switches to their Pi, and run simple software to either flash the LED, or detect that the push button has been pushed.

But why not make it more interesting? What about making a game of this simple hardware setup? There are other reaction measuring programs out on the internet, but none adapted to such a simple hardware setup.

Working with the Raspberry Pi should not only be educational, but **fun**!

#### Connecting the LED & Switch

Because the Pi requires basic current protection, a resister is used in series with *both* the push button and the LED

```
 BUTTON_PIN-----Button-----/\/\/\/---------o Gnd
                            1K ohm

```


And the LED:

```
 LED_PIN--------->+LED-<---/\/\/\/---------o Gnd
                            500 ohm

```

Using the handy Pi [pin out chart](https://en.wikipedia.org/wiki/Raspberry_Pi#General_purpose_input-output_(GPIO)_connector), one would determine two (2) GPIO (General Purpose Input/Output), and two (2) ground pins to use.




#### Running the Game

Because the Raspberry Pi GPIO is mapped directlly to memory (/dev/mem), more than likely **sudo** will have to be used to start the game from a terminal window.

```
sudo ./react.py
```

The game will blink the LED three (3) times to alert the player to be ready. Then the LED will go out for a random period between 1 and 5 seconds. It will light the LED solid, until the push button is pressed, end of round one. The game will repeat two more rounds, then print out the reaction times of each round.


#### But what if I don't have a Raspberry Pi?

The React game can be played in a terminal window, or via ssh (to any Linux computer). Using the `-k` (keyboard) `-n` (no LED) options it is possible to play in just a terminal.

```
./react.py -k -n
READY...
***GO***
READY...
***GO***
READY...
***GO***

Your times were:
481 milisecs
575 milisecs
360 milisecs

```

The `READY...` is just like the three blinks of the LED, alerting the gamer to be ready. Once the `***GO***` is seen, the gamer presses any key on the keyboard. As with the  *normal* play, there are three (3) rounds, and then the reaction times are printed.

When using the `-k -n` options, `sudo` is not required, as it does not utilize GPIO, and can run on any linux machine with Python3.



### Help
```
./react.py -h

 Reaction Time Game on the Pi

 Blinks LED (3x), then pauses signaling ready, then turns on LED
       Gamer presses button as quickly as possible, which turns off LED
	   Game measures reaction time, and prints after 3 rounds

 Options:
 	-k	use keyboard (instead of button)
	-n	don't use LED (instead print prompts)
	-d	display debug info

 Can be played on a non-Raspberry Pi with the -k -n options

```



## Installation

Install Python3, if not already installed.

On the Raspberry Pi, `raspian` should already have the GPIO python libraries already installed.

Edit `react.py` with your favourite editor, to use the `BOARD` pin outs of your LED and Switch.

```
##### Define the LED pin
LED_PIN = 40

##### Define the BUTTON PIN
BUTTON_PIN = 22
```


## Dependencies

React only requires Python3, all python libraries used should be included with the python 3 installation.

## Linux Containers?

Sure `react.py` can run inside a linux container. It was tested in an Alpine Linux v3.10 container on LXD version 3.21, running on `raspian buster` (aka version 10) on a Raspberry Pi 3b+.

The advantage of using a container, is the ease of back-up/restore, allowing one to try new things. If it doesn't work out, just `restore` the container from the last good `snapshot` and you are back up and running.

Of course, since GPIO is memory mapped, the container requires direct access to /dev/mem.

```
lxc config set <container name> raw.lxc 'lxc.cap.drop='
lxc config device add <container name> devmem unix-char source=/dev/mem
lxc restart <container>
```

It should be possible to run multiple containers, each running scripts which access GPIO, as long as you coordinate the GPIO pins used in each container (so they aren't wrestling over the same pins).

And have fun!

## Limitations

We don't need any stinking limitations.
 




## Contributors

All code by Craig Miller cvmiller at gmail dot com. But ideas, and ports to other embedded platforms are welcome. 


## License

This project is open source, under the GPLv2 license (see [LICENSE](LICENSE))
