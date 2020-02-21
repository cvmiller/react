#! /usr/bin/python

"""
 Reaction Time Game on the Pi

 Blinks LED (3x), then pauses signaling ready, then turns on LED
       Gamer presses button as quickly as possible, which turns off LED
       Game measures reaction time, and prints after 3 rounds

 Options:
     -k    use keyboard (instead of button)
    -n    don't use LED (instead print prompts)
    -d    display debug info

 Can be played on a non-Raspberry Pi with the -k -n options

 18 Feb 2020 by Craig Miller
 
 Version 0.8
"""

FALSE = 0
TRUE = not FALSE

DEBUG = FALSE
SHOW_ERRORS = FALSE

# use keyboard rather than button
USE_KBD = FALSE

# use display rather than LED
USE_LED = TRUE

# Import the libraries we need to flash LED
#import RPi.GPIO as GPIO
import time
import os
import getopt
import traceback
import random


#
# Set board pins to match your physical config 
#

##### Define the LED pin
#
# LED_PIN--------->+LED-<---/\/\/\/---------o Gnd
#                            500 ohm

LED_PIN = 40


##### Define the BUTTON PIN
#
# BUTTON_PIN-----Button-----/\/\/\/---------o Gnd
#                            1K ohm

BUTTON_PIN = 22



# Delays used in the game (small and biggest delay while waiting for the solid LED)
DELAY_SMALL = 1.5
DELAY_BIG   = 4.5
# delay used to blink the LED ready signal
DELAY_READY = 0.1


# get char from keyboard
import sys, termios, tty

#
# Blocking function to get any character from the keyboard
#

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return ch

# initialze the random module
random.seed()


#
# timer class, which supports start,stop,duration history
#

class mytime :
    def __init__ (self):
        self.history = []

    def clear (self):
        self.history = []

    def start (self):
        self.start_time = time.perf_counter()

    def stop (self):
        duration = time.perf_counter() - self.start_time
        # convert to miliseconds
        duration_milisec = int(duration * 1000)
        self.history.append(duration_milisec)
        return (duration_milisec)

    def show_hist(self):
        for item in self.history:
            print("%s milisecs" % (item))

    def rand_delay (self,a,b):
        # a is the smallest time, b is the largest time in Secs
        wait_time = random.uniform(a,b) 
        if DEBUG:
            print("wait time:%s" % (wait_time))
        time.sleep(wait_time)
        
        


#
# Handles button (or keyboard) events
#

class mybutton:
    def __init__(self,mode='btn',delay=50):
        global DEBUG, BUTTON_PIN
        
        self.UP = 0
        self.DOWN = not self.UP
        self.mode = mode
        self.delay = delay
        self.debug = DEBUG
        self.state = self.UP
        self.btn = BUTTON_PIN
        self.mode = mode
        if mode == 'btn':
            # Set up Switch as input with pull up resistor.
            GPIO.setup(self.btn, GPIO.IN, GPIO.PUD_UP)
        if self.debug:
            print("mybutton initialized")
    
    def setmode (self, mode):
        if mode == 'kbd':
            self.mode = 'kbd'
        else:
            self.mode = 'btn'

    def button_press (self):
        self.state = self.UP
        if self.mode == 'kbd':
            # blocking call, wait for keypress
            key = ord(getch())
            if key == 27: #ESC quit the game
                os._exit(0)
            self.state = self.DOWN
        if self.mode == 'btn':
            if DEBUG:
                print("waiting for button")
            # only detect button is down 
            binput = 1
            while binput == 1:
                binput = GPIO.input(self.btn)
                # short sleep to keep CPU from going 100%
                time.sleep(.01)
                if DEBUG and binput == 0:
                    print('Button pressed')    
                self.state = self.DOWN
        return (self.state)        

#
# Handles LED: init, flashing, turn on/off
#

class myled:
    def __init__(self,use_led=TRUE):
        global DEBUG, LED_PIN, DELAY_READY
        
        self.pin = LED_PIN
        self.ready = DELAY_READY
        self.use_led = use_led
        if use_led:
            # Set the pin to be an output
            GPIO.setup(LED_PIN, GPIO.OUT)
        self.off()

    def flash_ready(self):
        print("READY...")
        if self.use_led:
            # flash the LED for "ready signal"
            for i in range(0,3):
                GPIO.output(self.pin, 1)
                time.sleep(self.ready)
                GPIO.output(self.pin, 0)
                time.sleep(self.ready)

    def on (self):
        if self.use_led:
            GPIO.output(self.pin, 1)
        else:
            # allow screen-only play
            print("***GO***")

    def off (self):
        if self.use_led:
            GPIO.output(self.pin, 0)


def main ():
    global USE_KBD, USE_LED, DEBUG, LED_PIN, BUTTON_PIN, DELAY_SMALL, DELAY_BIG, DELAY_READY
    
    # initialze input method
    use_keyboard = 'btn'

    # get any command line options    
    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'h?dkn', ['help','h','?', 'debug','kbd','noled'])
    except Exception as e:
        print(str(e))
        exit_with_usage()

    command_line_options = dict(optlist)
    # There are a million ways to cry for help. These are but a few of them.
    if [elem for elem in command_line_options if elem in ['-h','--h','-?','--?','--help']]:
        exit_with_usage(0)

    # Parse the options, set vars as needed
    for the_opt in list(command_line_options.keys()):
        #process command line options to global vars
        if the_opt == '--skipdown':
            if str(command_line_options[the_opt]) != '':
                skipdown = str(command_line_options[the_opt])
            else:
                pass
        if the_opt == '--debug' or the_opt == '-d':    
            DEBUG = TRUE
        if the_opt == '--kbd' or the_opt == '-k':    
            USE_KBD = TRUE
            use_keyboard = 'kbd'
        if the_opt == '--noled' or the_opt == '-n':    
            USE_LED = FALSE

    # show the options (in debug)
    if DEBUG:
        for the_opt in list(command_line_options.keys()):
            # show options passed with a dictionary
            print("option=%s \t value=%s" % (the_opt, command_line_options[the_opt]))
        print('keyboard:%s' % (use_keyboard))
        
    # start main program, init vars
    count = 0

    #Initialize GPIO mode to BOARD, silence warnings
    if USE_LED:
        # use the GPIO library
        import RPi.GPIO as GPIO

        # silence the warnings
        GPIO.setwarnings(False)
        # Set the pin mode to board pin numbering
        GPIO.setmode(GPIO.BOARD)

    
    # initialize the button
    button = mybutton(use_keyboard)
        
    # initialize timer object
    timer = mytime()

    # initialize LED object
    led = myled(USE_LED)

    # main loop
    while count < 3:
        # flash the LED 3 times to tell the gamer we are ready
        led.flash_ready()
        
        # wait a random time for user to get relaxed
        timer.rand_delay(DELAY_SMALL,DELAY_BIG)
        
        # Let the game begin: light the LED, gamer press the button
        led.on()
        timer.start()
        
        # wait for button press
        result = button.button_press()
        if result and DEBUG:
            print('Main->button pressed')
        
        # stop the timer, record the time, and turn off the LED
        timer.stop()
        led.off()
        
        # increment the while loop counter
        count += 1
                
        # delay before going into next round while loop
        if count < 3:
            # pause before playing again
            time.sleep(DELAY_SMALL)
        
    # show results
    print("\nYour times were:")
    timer.show_hist()


def exit_with_usage(exit_code=2):
    # __doc_ prints the first comment at top of this script
    print(globals()['__doc__'])
    os._exit(exit_code)



if __name__ == '__main__':
    
    try:
        main()
        #self_test()
    except KeyboardInterrupt:
        print("Detected ^C")
        os._exit(1)
    except Exception as e:
        #print str(e)
        print("Exception Detected")
        print(str(e))
        traceback.print_exc()
        os._exit(1)
