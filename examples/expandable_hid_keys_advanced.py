# SPDX-FileCopyrightText: 2021 Sandy Macdonald
#
# SPDX-License-Identifier: MIT

# An advanced example of how to set up a HID keyboard.

# There are three layers, selected by pressing and holding key 0 (bottom left), 
# then tapping one of the coloured layer selector keys above it to switch layer.

# The layer RGB are as follows:

#  * layer 1: pink: numpad-style keys, 0-9, delete, and enter.
#  * layer 2: blue: sends strings on each key press
#  * layer 3: media controls, rev, play/pause, fwd on row one, vol. down, mute,
#             vol. up on row two
#MORE LAYERS SEE BELOW

# You'll need to connect Keybow 2040 to a computer, as you would with a regular
# USB keyboard.

# Drop the keybow2040.py file into your `lib` folder on your `CIRCUITPY` drive.

# NOTE! Requires the adafruit_hid CircuitPython library also!

import board
import time
from keybow2040 import Keybow2040

import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

# Set up Keybow
i2c = board.I2C()
keybow = Keybow2040(i2c)
keys = keybow.keys

# Set up the keyboard and layout
keyboard = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(keyboard)

# Set up consumer control (used to send media key presses)
consumer_control = ConsumerControl(usb_hid.devices)

# Our layers. The key of item in the layer dictionary is the key number on
# Keybow to map to, and the value is the key press to send.

# Note that key 0 is reserved as the modifier key 
# respectively.

#NUMPAD
layer_numpad_1 =  {
            4: Keycode.ZERO,
            1: Keycode.ONE,
            2: Keycode.FOUR,
            3: Keycode.SEVEN,
            5: Keycode.TWO,
            6: Keycode.FIVE,
            7: Keycode.EIGHT,
            8: Keycode.KEYPAD_ENTER,
            9: Keycode.THREE,
            10: Keycode.SIX,
            11: Keycode.NINE,
            12: Keycode.KEYPAD_PLUS, #PLUS
            13: Keycode.KEYPAD_MINUS,
            14: Keycode.KEYPAD_ASTERISK, #MULTIPLY
            15: Keycode.KEYPAD_FORWARD_SLASH
            }


# MACRO Strings
layer_strings_2 =  {
            3: "Quick",
            2: "prince",
            1: "Lol",
            7: "Geeks",
            11: "N3rd",
            15: "Rule",
            6: "Enginerd",
            10: "7$\n",
            14: "MSin",
            5: "M$of",
            9: "Sphinx of ",
            12: "Black ",
            4: "Quartz ",
            8: "Judge ",
            13: "my Vow.\n"
            }

# MEDIA CONTROLS
layer_3 =  {
            6: ConsumerControlCode.VOLUME_DECREMENT,
            7: ConsumerControlCode.SCAN_PREVIOUS_TRACK,
            10: ConsumerControlCode.MUTE,
            11: ConsumerControlCode.PLAY_PAUSE,
            14: ConsumerControlCode.VOLUME_INCREMENT,
            15: ConsumerControlCode.SCAN_NEXT_TRACK}
##---------------------------
##|    |<<  |Play/Pause|>>  |
##---------------------------
##|    |Vol-|MUTE      |Vol+|
##---------------------------
##|    |    |          |    |
##---------------------------
##|MOD*|    |          |    |
##---------------------------

# WINDOWS SHORTCUTS
layer_4_shortcuts = { 
            1: [Keycode.CONTROL, Keycode.S], #save
            2: [Keycode.CONTROL, Keycode.C], #copy
            3: [Keycode.CONTROL, Keycode.V], #paste
            4: [Keycode.ALT, Keycode.SHIFT, Keycode.TAB], #switch active app
            5: [Keycode.GUI, Keycode.PERIOD], #Emoji Keyboard
            6: [Keycode.CONTROL, Keycode.X], #cut
            7: [Keycode.CONTROL, Keycode.A], #select all
            8: [Keycode.GUI, Keycode.SHIFT, Keycode.RIGHT_ARROW], # Move app to next monitor
            9: [Keycode.GUI, Keycode.UP_ARROW], #Maximize
            10: [Keycode.GUI, Keycode.DOWN_ARROW], #Minimize
            11: Keycode.HOME,
            12: [Keycode.GUI, Keycode.L], #Lock screen
            13: Keycode.PAGE_UP, # Page up
            14: Keycode.PAGE_DOWN, # Page down
            15: Keycode.END
}
##|---------------------
##|PASTE|All |HOME|END
##|---------------------
##|COPY |CUT |min |PgUp
##|---------------------
##|SAVE |EMoj|MAX |PgDn
##|---------------------
##|MOD* |APP |Mov |LOCK
##|---------------------


# Microsoft Teams Shortcuts
layer_5_teams_cuts = {
            2: [Keycode.CONTROL, Keycode.TWO], #Teams Chat
            1: [Keycode.CONTROL, Keycode.THREE], # Teams Calendar
            4: [Keycode.ALT, Keycode.SHIFT, Keycode.TAB], #switch active app
            3: [Keycode.CONTROL, Keycode.SHIFT, Keycode.M], #Teams Toggle Mute
            6: [Keycode.CONTROL, Keycode.SHIFT, Keycode.E], #Share screen
            12: [Keycode.CONTROL, Keycode.SHIFT, Keycode.B], # Leave Meeting
            7: [Keycode.CONTROL, Keycode.SHIFT, Keycode.O], #Teams Toggle Video
            11: [Keycode.CONTROL, Keycode.SHIFT, Keycode.S], #Accept call
            15: [Keycode.CONTROL, Keycode.SHIFT, Keycode.A], #Accept video
            10: [Keycode.CONTROL, Keycode.SHIFT, Keycode.D], #decline call
            14: [Keycode.CONTROL, Keycode.SHIFT, Keycode.K] #RAISE LOWER HAND
            }
##----------------------------
##|MUTE|VID  |A_call|A_vid|
##----------------------------
##|CHAT|SHARE|D_call|HAND |
##----------------------------
##|CALE|     |      |     |
##----------------------------
##|MOD*|APP  |      |LEAVE|
##----------------------------

layers =      {1: layer_numpad_1,
               2: layer_strings_2,
               3: layer_3,
               4: layer_4_shortcuts,
               5: layer_5_teams_cuts}

# Define the modifier key and layer selector keys
modifier = keys[0]
mod_on = True

selectors =   {1: keys[1],
               2: keys[2],
               3: keys[3],
               4: keys[4],
               5: keys[5]}

# Start on layer 1
current_layer = 1

# The RGB for each layer
RGB = {1: (255, 0, 255),
           2: (0, 255, 255),
           3: (255, 255, 0),
           4: (20, 230, 50),
           5: (80, 90, 201)}

layer_keys = range(1, 16)

# Set the LEDs for each key in the current layer
for k in layers[current_layer].keys():
    keys[k].set_led(*RGB[current_layer])

# To prevent the strings (as opposed to single key presses) that are sent from 
# refiring on a single key press, the debounce time for the strings has to be 
# longer.
short_debounce = 0.03
long_debounce = 0.15
debounce = 0.03
fired = False

while True:
    # Always remember to call keybow.update()!
    keybow.update()

    # This handles the modifier and layer selector behaviour
    if modifier.held:
        # Give some visual feedback for the modifier key
        if not mod_on:
            mod_on = True
        keys[0].led_off()

        # If the modifier key is held, light up the layer selector keys
        for layer in layers.keys():
            keys[layer].set_led(*RGB[layer])

            # Change layer if layer key is pressed
            if current_layer != layer:
                if selectors[layer].pressed:
                    current_layer = layer

                    #any keys defined as layer key that are pressed while holding mod set to unpressed
                    selectors[layer].pressed = False

                    # Set the key LEDs first to off, then to their layer colour
                    for k in layer_keys:
                        keys[k].set_led(0, 0, 0)

                    for k in layers[layer].keys():
                        keys[k].set_led(*RGB[layer])

    # Turn off the layer selector LEDs if the modifier isn't held
    else:
        # we want to reset the colors of the layer keys if we are no longer holding the modifier key
        if mod_on:
            mod_on = False
            for k in selectors.keys():
                keys[k].led_off()
                if k in layers[current_layer].keys():
                    keys[k].set_led(*RGB[current_layer])
        # Give some visual feedback for the modifier key
        keys[0].set_led(0, 255, 25)

    # Loop through all of the keys in the layer and if they're pressed, get the
    # key code from the layer's key map
    if not modifier.held: #Makes it so chosing layer does not trigger keypresses
        for k in layers[current_layer].keys():
            if keys[k].pressed:
                key_press = layers[current_layer][k]

            # If the key hasn't just fired (prevents refiring)
                if not fired:
                    fired = True

                # Send the right sort of key press and set debounce for each
                # layer accordingly (layer 2 needs a long debounce)
                    if current_layer == 1: #single keys
                        debounce = short_debounce
                        keyboard.send(key_press)
                    elif current_layer == 2: #Strings
                        debounce = long_debounce
                        layout.write(key_press)
                    elif current_layer == 3: #Media controls
                        debounce = short_debounce
                        consumer_control.send(key_press)
                    elif current_layer >= 4 and current_layer <= 5: #For use with single keys or shortcuts
                        debounce = short_debounce
                        if isinstance(key_press, list):
                            keyboard.send(*key_press)
                        else:
                            keyboard.send(key_press)


    # If enough time has passed, reset the fired variable
    if fired and time.monotonic() - keybow.time_of_last_press > debounce:
        fired = False
        