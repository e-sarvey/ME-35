import paho.mqtt.client as mqtt
import time
import matplotlib.pyplot as plt
import numpy as np
from math import cos, sin, atan2, sqrt, pi, acos, degrees

def invkin(x_e=0.7, y_e=0.4, L = [1, 1], x_0=0, y_0=0):
    
    R_end = sqrt( (x_e - x_0)**2 + (y_e - y_0)**2 )
    R_arm = L[0] + L[1]
    
    if R_end > R_arm:
        print('location is outside range of arm')
        return
    
    # inputs: x and y end efector location, list with lengths of arms, x and y origin shift
    # Calculate the angles:
    beta = atan2((y_e - y_0), (x_e - x_0))
    d = sqrt((x_e - x_0)**2 + (y_e - y_0)**2)
    cos_a = (L[0]**2 + d**2 - L[1]**2) / (2 * L[0] * d)
    alpha = atan2(sqrt(1 - cos_a**2), cos_a)
    theta_1 = alpha + beta
    cos_g = (L[0]**2 + L[1]**2 - d**2) / (2 * L[0] * L[1])
    gamma = atan2(sqrt(1 - cos_g**2), cos_g)
    theta_2 = -1*(pi - gamma) # this was the problem term. seems to have something to do with assuming theta 2 is negative in derivation

    # Use FWD kinematics to find joint position for plotting and confirm angles result in correct end effector location
    x_1 = x_0 + L[0] * cos(theta_1)
    y_1 = y_0 + L[0] * sin(theta_1)
    x_e_check = x_1 + L[1] * cos(theta_1 + theta_2)
    y_e_check = y_1 + L[1] * sin(theta_1 + theta_2)

    # Calculate error between desired and resulting end effector location based on angles caluclate
    # used to verify angle calculations and de-bug
    error_x = x_e_check - x_e
    error_y = y_e_check - y_e

    # Print information for debug
#     print(f"End effector location: ({x_e},{y_e})")
#     print(f"Angles: theta_1 = {degrees(theta_1)}, theta_2 = {degrees(theta_2)}")
#     print(f"Error_x: {round(error_x,4)}")
#     print(f"Error_y: {round(error_y,4)}")

    # put results in a list for easy return
    res = [degrees(theta_1), degrees(theta_2)]
    return res


## MAIN ##    
x_0, y_0 = 0, 0  # Origin
d = 1 # length of arm and center and diameter of circle drawn
L = [d, d]       # Lengths of arms

# calculate list of end positions that make a circle
pts = 100
x_e = np.linspace(d/2, 1.5*d, pts).tolist() # define end efector domain
x_e_rev = list(reversed(x_e))

y_pos = []
y_neg = []

# calculate the points in a full circle: +/- y values
for x in x_e:
    y_new = sqrt( (d/2)**2 - (x - d)**2 )
    y_pos.append(y_new)

for x in x_e_rev:
    y_new = -sqrt( (d/2)**2 - (x - d)**2 )
    y_neg.append(y_new)

# concat arrays for +/- y values and turn into np.array type to try vertical concat
x_e = np.array(x_e + x_e_rev)
y_e = np.array(y_pos + y_neg)

circle = np.vstack((x_e,y_e)) # not necessary, just playing around with np arrays to compare to MATLAB
columns = circle.shape[1]

theta_1, theta_2 = [], []
for i in range(columns):
    res = invkin(circle[0,i], circle[1,i], L) # calculate the IK for every point in the circle
    theta_1.append(res[0])
    theta_2.append(res[1])
    #print(res) # uncomment to see full list of arm1 and arm2 angles as they generate
    
# set up MQTT
broker = '127.0.0.1' # Change this to Chris's IP. Local IP for running on laptop: 127.0.0.1
topic1 = 'ME035' # Change this to the topic chosen
#topic2 = 'wait' # need to determine what this means in class tomorrow morning? Do we post a single value or one each iteration
client_name = 'elijah_client'
pub_wait = 0.1

# subscribe and publish angles
client = mqtt.Client(client_name)
client.connect(broker)
print(f'connected to broker at {broker} as {client_name}')

for i in range(columns):
    # publish a pair of angles (theta_1, theta_2) for each point in circle based on list calculated previously
    data = f'({round(theta_1[i],2)},{round(theta_2[i],2)})'
    client.publish(topic1, data)
    print(data) # uncomment to see the values being published
    time.sleep(pub_wait) # wait before publishing next value

