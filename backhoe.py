import time
import machine
import mqtt
import network, ubinascii
from machine import Pin, PWM

#connect to wifi
ssid = 'Tufts_Wireless'
password = ''

def connect_wifi(ssid, password):
    station = network.WLAN(network.STA_IF)
    station.active(True)
    mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
    print("MAC " + mac)
    
    station.connect(ssid, password)
    while not station.isconnected():
        time.sleep(1)
    print('Connection successful')
    print(station.ifconfig())

#initialize motors
leftFront_servo=PWM(Pin(2))
leftFront_servo.freq(50)

rightFront_servo=PWM(Pin(15)) 
rightFront_servo.freq(50)

leftBack_servo = PWM(Pin(3)) 
leftBack_servo.freq(50)

rightBack_servo = PWM(Pin(14)) 
rightBack_servo.freq(50)

armOne_servo = PWM(Pin(12)) 
armOne_servo.freq(50)

armTwo_servo = PWM(Pin(0)) 
armTwo_servo.freq(50)

grab_servo = PWM(Pin(5)) 
grab_servo.freq(50)

#turns string mqtt message to an int duty cycle
def convertDuty(string):
    x = int(string)
    x = x * 10000
    return int(x)

def carMove(string):
    g = 0
    fl = 0
    fr = 0
    bl = 0
    br = 0
    if string == "Forward":
        print("forward")
        fl = 2_500_000
        fr = 1_000_000
        bl = 1_000_000
        br = 1_000_000
        
        
    elif string == "Left":
        print("left")
        fl = 0
        fr = 1_000_000
        bl = 0
        br = 1_000_000
        
    elif string == "Right":
        fl = 2_500_000
        fr = 0
        bl = 1_000_000
        br = 0
        
        print("right")
    elif string == "Backward":
        print("backward")
        fl = 750_000
        fr = 2_500_000
        bl = 0
        br = 0
         
    elif string == "Stop":
        print("stop")
        fl = 0
        fr = 0
        bl = 0
        br = 0
        
    elif string == "Drop":
        print("Drop")
        g = 180
        grab_servo.duty_ns(int(g*10000))
    elif string == "Grab":
        print("Grab")
        g = 250
        grab_servo.duty_ns(int(g*10000))
        
    leftFront_servo.duty_ns(fl)
    rightFront_servo.duty_ns(fr)
    leftBack_servo.duty_ns(bl) 
    rightBack_servo.duty_ns(br)
    time.sleep(0.25)
    leftFront_servo.duty_ns(0)
    rightFront_servo.duty_ns(0)
    leftBack_servo.duty_ns(0) 
    rightBack_servo.duty_ns(0)

#interpret mqtt message to motor action
def whenCalled(topic, msg): # want to attempt making three separate callbacks if lagging
    message = msg.decode()
    topic = topic.decode()
    angleOne = 0
    angleTwo = 0
    if topic == "ArmOne":
        print("arm one")
        angleOne = convertDuty(message)
        armOne_servo.duty_ns(angleOne)
        time.sleep(1)
        print(angleOne)
    elif topic == "ArmTwo":
        angleTwo = convertDuty(message)
        armTwo_servo.duty_ns(angleTwo)
        time.sleep(1)
        print(angleTwo)
    elif topic == "ME035":
        carMove(message)
            
def main():
    try:
        driver = mqtt.MQTTClient("GoPhillies", "10.243.28.115", keepalive=60)
        print('Connected')
        driver.connect()
        driver.set_callback(whenCalled)
    except OSError as e:
        print('Failed')
        return
    driver.subscribe("ME035")
    driver.subscribe("ArmOne")
    driver.subscribe("ArmTwo")
    
    try:
        while True:
            driver.check_msg() 
            time.sleep(0.01)
    except Exception as e:
        print(e)
    finally:
        leftFront_servo.deinit()
        rightFront_servo.deinit()
        leftBack_servo.deinit()
        rightBack_servo.deinit()
        armOne_servo.deinit()
        armTwo_servo.deinit()
        grab_servo.deinit()
        driver.disconnect()
        
        print('done')

connect_wifi(ssid, password)
main()