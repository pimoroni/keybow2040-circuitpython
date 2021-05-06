# SPDX-FileCopyrightText: 2021 Sandy Macdonald
#
# SPDX-License-Identifier: MIT

"""
`Keybow 2040 CircuitPython library`
====================================================

CircuitPython driver for the Pimoroni Keybow 2040.

Drop the keybow2040.py file into your `lib` folder on your `CIRCUITPY` drive.

* Author: Sandy Macdonald

Notes
--------------------

**Hardware:**

* Pimoroni Keybow 2040
  <https://shop.pimoroni.com/products/keybow-2040>_

**Software and Dependencies:**

* Adafruit CircuitPython firmware for Keybow 2040:
  <https://circuitpython.org/board/pimoroni_keybow2040/>_

* Adafruit CircuitPython IS31FL3731 library:
  <https://github.com/adafruit/Adafruit_CircuitPython_IS31FL3731>_
"""

import time
import board

from adafruit_is31fl3731.keybow2040 import Keybow2040 as Display
from digitalio import DigitalInOut, Direction, Pull

# These are the 16 switches on Keybow, with their board-defined names.
_PINS = [board.SW0,
        board.SW1,
        board.SW2,
        board.SW3,
        board.SW4,
        board.SW5,
        board.SW6,
        board.SW7,
        board.SW8,
        board.SW9,
        board.SW10,
        board.SW11,
        board.SW12,
        board.SW13,
        board.SW14,
        board.SW15]

NUM_KEYS = 16


class Keybow2040(object):
    """
    Represents a Keybow 2040 and hence a set of Key instances with
    associated LEDs and key behaviours.

    :param i2c: the I2C bus for Keybow 2040
    """
    def __init__(self, i2c):
        self.pins = _PINS
        self.display = Display(i2c)
        self.keys = []
        self.time_of_last_press = time.monotonic()
        self.time_since_last_press = None
        self.led_sleep_enabled = False
        self.led_sleep_time = 60
        self.sleeping = False
        self.was_asleep = False
        self.last_led_states = None
        # self.rotation = 0

        for i in range(len(self.pins)):
            _key = Key(i, self.pins[i], self.display)
            self.keys.append(_key)

    def update(self):
        # Call this in each iteration of your while loop to update
        # to update everything's state, e.g. `keybow.update()`

        for _key in self.keys:
            _key.update()

        # Used to work out the sleep behaviour, by keeping track
        # of the time of the last key press.
        if self.any_pressed():
            self.time_of_last_press = time.monotonic()
            self.sleeping = False

        self.time_since_last_press = time.monotonic() - self.time_of_last_press

        # If LED sleep is enabled, but not engaged, check if enough time
        # has elapsed to engage sleep. If engaged, record the state of the
        # LEDs, so it can be restored on wake.
        if self.led_sleep_enabled and not self.sleeping:
            if time.monotonic() - self.time_of_last_press > self.led_sleep_time:
                self.sleeping = True
                self.last_led_states = [k.rgb if k.lit else [0, 0, 0] for k in self.keys]
                self.set_all(0, 0, 0)
                self.was_asleep = True

        # If it was sleeping, but is no longer, then restore LED states.
        if not self.sleeping and self.was_asleep:
            for k in range(len(self.keys)):
                self.keys[k].set_led(*self.last_led_states[k])
            self.was_asleep = False

    def set_led(self, number, r, g, b):
        # Set an individual key's LED to an RGB value by its number.

        self.keys[number].set_led(r, g, b)

    def set_all(self, r, g, b):
        # Set all of Keybow's LEDs to an RGB value.

        if not self.sleeping:
            for _key in self.keys:
                _key.set_led(r, g, b)
        else:
            for _key in self.keys:
                _key.led_off()

    def get_states(self):
        # Returns a Boolean list of Keybow's key states
        # (0=not pressed, 1=pressed).

        _states = [_key.state for _key in self.keys]
        return _states

    def get_pressed(self):
        # Returns a list of key numbers currently pressed.

        _pressed = [_key.number for _key in self.keys if _key.state == True]
        return _pressed

    def any_pressed(self):
        # Returns True if any key is pressed, False if none are pressed.

        if any(self.get_states()):
            return True
        else:
            return False

    def none_pressed(self):
        # Returns True if none of the keys are pressed, False is any key
        # is pressed.

        if not any(self.get_states()):
            return True
        else:
            return False

    def on_press(self, _key, handler=None):
        # Attaches a press function to a key, via a decorator. This is stored as
        # `key.press_function` in the key's attributes, and run if necessary
        # as part of the key's update function (and hence Keybow's update
        # function). It can be attached as follows:

        # @keybow.on_press(key)
        # def press_handler(key, pressed):
        #     if pressed:
        #         do something
        #     else:
        #         do something else

        if _key is None:
            return

        def attach_handler(handler):
            _key.press_function = handler

        if handler is not None:
            attach_handler(handler)
        else:
            return attach_handler

    def on_release(self, _key, handler=None):
        # Attaches a release function to a key, via a decorator. This is stored
        # as `key.release_function` in the key's attributes, and run if
        # necessary as part of the key's update function (and hence Keybow's
        # update function). It can be attached as follows:

        # @keybow.on_release(key)
        # def release_handler(key):
        #     do something

        if _key is None:
            return

        def attach_handler(handler):
            _key.release_function = handler

        if handler is not None:
            attach_handler(handler)
        else:
            return attach_handler

    def on_hold(self, _key, handler=None):
        # Attaches a hold unction to a key, via a decorator. This is stored as
        # `key.hold_function` in the key's attributes, and run if necessary
        # as part of the key's update function (and hence Keybow's update
        # function). It can be attached as follows:

        # @keybow.on_hold(key)
        # def hold_handler(key):
        #     do something

        if _key is None:
            return

        def attach_handler(handler):
            _key.hold_function = handler

        if handler is not None:
            attach_handler(handler)
        else:
            return attach_handler

    def rotate(self, degrees):
        try:
            print(degrees)
            num_rotations = degrees // 90

            if num_rotations < 1:
                num_rotations = 4 + num_rotations

            col_length = 4
            rotations_performed = 0
            print(num_rotations)

            if num_rotations > 0:
                resultArray = [None] * len(self.keys)
                while rotations_performed < num_rotations:
                    i = 0
                    while i < col_length:
                        print('i= ', i)
                        j = 0
                        while j < col_length:
                            print('j= ', j)
                            resultArray[i * col_length +
                                        j] = self.keys[(col_length - j - 1) * col_length + i]
                            j += 1
                        i += 1

                    key_nums = []
                    for i in range(0, len(resultArray)):
                        key_nums.append(resultArray[i].number)

                    for i in range(0, len(key_nums)):
                        self.keys[i].number = key_nums[i]

                    rotations_performed +=1
                    print("rotations", rotations_performed)

                print("rotation done")
        except Exception as e:
            print("Exception", e)

    # def rotate(self, degrees):
    #     # Rotates all of Keybow's keys by a number of degrees, clamped to
    #     # the closest multiple of 90 degrees. Because it shuffles the order
    #     # of the Key instances, all of the associated attributes of the key
    #     # are retained. The x/y coordinate of the keys are rotated also. It
    #     # also handles negative degrees, e.g. -90 to rotate 90 degrees anti-
    #     # clockwise.

    #     # Rotate as follows: `keybow.rotate(270)`

    #     self.rotation = degrees
    #     num_rotations = degrees // 90

    #     if num_rotations == 0:
    #         return

    #     if num_rotations < 1:
    #         num_rotations = 4 + num_rotations

    #     matrix = [[(x * 4) + y for y in range(4)] for x in range(4)]

    #     for r in range(num_rotations):
    #         matrix = zip(*matrix[::-1])
    #         matrix = [list(x) for x in list(matrix)]

    #     flat_matrix = [x for y in matrix for x in y]

    #     for i in range(len(self.keys)):
    #         self.keys[i].number = flat_matrix[i]

    #     self.keys = sorted(self.keys, key=lambda x:x.number)


class Key:
    """
    Represents a key on Keybow 2040, with associated switch and
    LED behaviours.

    :param number: the key number (0-15) to associate with the key
    :param pin: the pin object for the key, e.g. board.SW0
    :param display: the IS31FL3731 matrix instance for the LEDs
    """
    def __init__(self, number, pin, display):
        self.pin = pin
        self.number = number
        self.switch = DigitalInOut(self.pin)
        self.switch.direction = Direction.INPUT
        self.switch.pull = Pull.UP
        self.state = 0
        self.pressed = 0
        self.last_state = None
        self.time_of_last_press = time.monotonic()
        self.time_since_last_press = None
        self.time_held_for = 0
        self.held = False
        self.hold_time = 0.75
        self.modifier = False
        self.rgb = [0, 0, 0]
        self.lit = False
        self.xy = self.get_xy()
        self.x, self.y = self.xy
        self.display = display
        self.led_off()
        self.press_function = None
        self.release_function = None
        self.hold_function = None
        self.press_func_fired = False
        self.hold_func_fired = False
        self.debounce = 0.125
        self.key_locked = False

    def get_state(self):
        # Returns the state of the key (0=not pressed, 1=pressed).

        return int(not self.switch.value)

    def update(self):
        # Updates the state of the key and updates all of its
        # attributes.

        self.time_since_last_press = time.monotonic() - self.time_of_last_press

        # Keys get locked during the debounce time.
        if self.time_since_last_press < self.debounce:
            self.key_locked = True
        else:
            self.key_locked = False

        self.state = self.get_state()
        self.pressed = self.state
        update_time = time.monotonic()

        # If there's a `press_function` attached, then call it,
        # returning the key object and the pressed state.
        if self.press_function is not None and self.pressed and not self.press_func_fired and not self.key_locked:
            self.press_function(self)
            self.press_func_fired = True
            # time.sleep(0.05)  # A little debounce

        # If the key has been pressed and releases, then call
        # the `release_function`, if one is attached.
        if not self.pressed and self.last_state == True:
            if self.release_function is not None:
                self.release_function(self)
            self.last_state = False
            self.press_func_fired = False

        if not self.pressed:
            self.time_held_for = 0
            self.last_state = False

        # If the key has just been pressed, then record the
        # `time_of_last_press`, and update last_state.
        elif self.pressed and self.last_state == False:
            self.time_of_last_press = update_time
            self.last_state = True

        # If the key is pressed and held, then update the
        # `time_held_for` variable.
        elif self.pressed and self.last_state == True:
            self.time_held_for = update_time - self.time_of_last_press
            self.last_state = True

        # If the `hold_time` theshold is crossed, then call the
        # `hold_function` if one is attached. The `hold_func_fired`
        # ensures that the function is only called once.
        if self.time_held_for > self.hold_time:
            self.held = True
            if self.hold_function is not None and not self.hold_func_fired:
                self.hold_function(self)
                self.hold_func_fired = True
        else:
            self.held = False
            self.hold_func_fired = False

    def get_xy(self):
        # Returns the x/y coordinate of a key from 0,0 to 3,3.

        return number_to_xy(self.number)

    def get_number(self):
        # Returns the key number, from 0 to 15.

        return xy_to_number(self.x, self.y)

    def is_modifier(self):
        # Designates a modifier key, so you can hold the modifier
        # and tap another key to trigger additional behaviours.

        if self.modifier:
            return True
        else:
            return False

    def set_led(self, r, g, b):
        # Set this key's LED to an RGB value.

        if [r, g, b] == [0, 0, 0]:
            self.lit = False
        else:
            self.lit = True
            self.rgb = [r, g, b]

        self.display.pixelrgb(self.x, self.y, r, g, b)

    def led_on(self):
        # Turn the LED on, using its current RGB value.

        r, g, b = self.rgb
        self.set_led(r, g, b)

    def led_off(self):
        # Turn the LED off.

        self.set_led(0, 0, 0)

    def led_state(self, state):
        # Set the LED's state (0=off, 1=on)

        state = int(state)

        if state == 0:
            self.led_off()
        elif state == 1:
            self.led_on()
        else:
            return

    def toggle_led(self, rgb=None):
        # Toggle the LED's state, retaining its RGB value for when it's toggled
        # back on. Can also be passed an RGB tuple to set the colour as part of
        # the toggle.

        if rgb is not None:
            self.rgb = rgb
        if self.lit:
            self.led_off()
        else:
            self.led_on()

    def __str__(self):
        # When printed, show the key's state (0 or 1).
        return self.state

def xy_to_number(x, y):
    # Convert an x/y coordinate to key number.
    return x + (y * 4)

def number_to_xy(number):
    # Convert a number to an x/y coordinate.
    x = number % 4
    y = number // 4

    return (x, y)

def hsv_to_rgb(h, s, v):
    # Convert an HSV (0.0-1.0) colour to RGB (0-255)
    if s == 0.0:
        rgb = [v, v, v]

    i = int(h * 6.0)

    f = (h*6.)-i; p,q,t = v*(1.-s), v*(1.-s*f), v*(1.-s*(1.-f)); i%=6

    if i == 0:
        rgb = [v, t, p]
    if i == 1:
        rgb = [q, v, p]
    if i == 2:
        rgb = [p, v, t]
    if i == 3:
        rgb = [p, q, v]
    if i == 4:
        rgb = [t, p, v]
    if i == 5:
        rgb = [v, p, q]

    rgb = tuple(int(c * 255) for c in rgb)

    return rgb
