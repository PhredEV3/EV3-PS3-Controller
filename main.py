#!/usr/bin/env python3


import evdev
import ev3dev.auto as ev3
import threading
from ev3dev2.sound import Sound
sound = Sound()

## Some helpers ##
def scale(val, src, dst):
    """
    Scale the given value from the scale of src to the scale of dst.

    val: float or int
    src: tuple
    dst: tuple

    example: print(scale(99, (0.0, 99.0), (-1.0, +1.0)))
    """
    return (float(val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0]

def scale_stick(value):
    return scale(value,(0,255),(-100,100))

def clamp(value, floor=-100, ceil=100):
    """
    Clamp the value within the floor and ceiling values.
    """
    return max(min(value, ceil), floor)

## Initializing ##
print("Finding ps3 controller...")
devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
for device in devices:
    if device.name == 'PLAYSTATION(R)3 Controller':
        ps3dev = device.fn

gamepad = evdev.InputDevice(ps3dev)

# Initialize globals
speed = 0
turn = 0
running = True

# Within this thread all the motor magic happens
class MotorThread(threading.Thread):
    def __init__(self):
        # Add more sensors and motors here if you need them
        self.left_motor = ev3.LargeMotor(ev3.OUTPUT_B)
        self.right_motor = ev3.LargeMotor(ev3.OUTPUT_C)
        threading.Thread.__init__(self)

    def run(self):
        print("Engine running!")
        # Change this function to suit your robot. 
        # The code below is for driving a simple tank.
        while running:
            right_dc = clamp(-speed-turn)
            left_dc = clamp(-speed+turn)
            self.right_motor.run_direct(duty_cycle_sp=right_dc)
            self.left_motor.run_direct(duty_cycle_sp=left_dc)



        self.motor.stop()

# Multithreading magics
motor_thread = MotorThread()
motor_thread.setDaemon(True)
motor_thread.start()


for event in gamepad.read_loop():   #this loops infinitely
    if event.type == 3:             #One of the sticks is moved
        # Add if clauses here to catch more values for your robot.
        if event.code == 4:         #Y axis on right stick
            speed = scale_stick(event.value)
        if event.code == 3:         #X axis on right stick
            turn = scale_stick(event.value)

    if event.type == 1 and event.code == 304 and event.value == 1:
        print("X button is pressed. Stopping.")
        running = False
        break
    if event.type == 1 and event.code == 545 and event.value == 1:
        print("D-pad down pressed")
        sound.play_file('/home/robot/sounds/sounds/Hello.wav')
    if event.type == 1 and event.code == 544 and event.value == 1:
        print("D-pad up pressed")
        sound.play_file('/home/robot/sounds/sounds/Goodbye.wav')