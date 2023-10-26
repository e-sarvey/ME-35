#credit to https://docs.python.org/3/library/tkinter.ttk.html for help learning API controls

from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import paho.mqtt.client as mqtt
import tkinter as tk
import time

#connect to broker
broker_address = ("10.247.52.50")
client = mqtt.Client("KelliKowalick")
client.connect(broker_address)
client.subscribe("ME035")
#create UI
root = Tk()
frm = ttk.Frame(root, padding=10)
frm.grid()
style = ttk.Style()

#buttons change colors
style.map("C.TButton",
    foreground=[('pressed', 'red'), ('active', 'blue')],
    background=[('pressed', '!disabled', 'black'), ('active', 'white')]
    )

#create callbacks for buttons
def forward():
    client.publish("ME035", "Forward")
    time.sleep(0.1)

def backward():
    client.publish("ME035", "Backward")
    time.sleep(0.1)
    
def left():
    client.publish("ME035", "Left")
    time.sleep(0.1)

def right():
    client.publish("ME035", "Right")
    time.sleep(0.1)
    
def left():
    client.publish("ME035", "Left")
    time.sleep(0.1)
    
def stop():
    client.publish("ME035", "Stop")
    time.sleep(0.1)
    
def lower():
    client.publish("ME035", "Lower")
    time.sleep(0.1)
    
def lift():
    client.publish("ME035", "Lift")
    time.sleep(0.1)
   
def doneMessage():
    messagebox.showinfo(title='Result', message="Operation Complete!")
    
def drop():
    doneMessage()
    client.publish("ME035", "Drop")
    time.sleep(0.1)

def grab():
    client.publish("ME035", "Grab")
    time.sleep(0.1)

current_value = tk.StringVar()
current_value2 = tk.StringVar()

def angleOne():
    angle_value = current_value.get()
    client.publish("ArmOne", angle_value)
    time.sleep(0.1)
    
def angleTwo():
    angle_value = current_value2.get()
    client.publish("ArmTwo", angle_value)
    time.sleep(0.1)

#create UI controls
ttk.Label(frm, text="Robot Controls").grid(column=1, row=0)
ForwardBtn = ttk.Button(frm, text="Forward", style="C.TButton", command=forward).grid(column=1, row=1)
BackwardBtn = ttk.Button(frm, text="Backward", style="C.TButton", command=backward).grid(column=1, row=2)
LeftBtn = ttk.Button(frm, text="Left", style="C.TButton",command=left).grid(column=0, row=2)
RightBtn = ttk.Button(frm, text="Right", style="C.TButton", command=right).grid(column=2, row=2)
StopBtn = ttk.Button(frm, text="Emergency Break", style="C.TButton", command=stop).grid(column=1, row=3)
DropBtn = ttk.Button(frm, text="Release", style="C.TButton", command=drop).grid(column=0, row=6)
GrabBtn = ttk.Button(frm, text="Pick Up", style="C.TButton", command=grab).grid(column=2, row=6)
ttk.Label(frm, text="Arm One Angle (180-260):").grid(column=0, row=4)
ArmOneEnter = ttk.Entry(frm, textvariable=current_value).grid(column=1, row=4)
ArmOneButton = ttk.Button(frm, text="Enter", style="C.TButton", command=angleOne).grid(column=2, row=4)
ttk.Label(frm, text="Arm Two Angle (65-140):").grid(column=0, row=5)
ArmTwoEnter = ttk.Entry(frm, textvariable=current_value2).grid(column=1, row=5)

root.mainloop()
