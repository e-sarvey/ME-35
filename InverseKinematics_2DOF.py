import matplotlib.pyplot as plt
import numpy as np
from math import cos, sin, atan2, sqrt, pi, acos, degrees
from matplotlib.animation import FuncAnimation, Animation

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
    res = [theta_1, theta_2, x_1, y_1]
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

for x in x_e:
    y_new = sqrt( (d/2)**2 - (x - d)**2 )
    y_pos.append(y_new)

for x in x_e_rev:
    y_new = -sqrt( (d/2)**2 - (x - d)**2 )
    y_neg.append(y_new)

x_e = np.array(x_e + x_e_rev)
y_e = np.array(y_pos + y_neg)

circle = np.vstack((x_e,y_e))
columns = circle.shape[1]

# Create a figure and axis for the animation
fig, ax = plt.subplots()
line_lower, = ax.plot([], [], marker='o', markersize=5, color='g') # initiate the lower segment of the arm
line_upper, = ax.plot([], [], marker='o', markersize=5, color='r') # initiate the upper segment of the arm
path_line, = ax.plot([], [], linestyle='--', color='k')	# intiate the end effector path animation

theta1_text = ax.text(0.8, 1.5, 'θ₁', fontsize=12)	# initiate labels for the angles
theta2_text = ax.text(0.8, 1.3, 'θ₂', fontsize=12)

def init():
    line_lower.set_data([], [])
    line_upper.set_data([], [])
    path_line.set_data([], [])
    return line_lower, line_upper, path_line

def animate(i):
    res = invkin(circle[0, i], circle[1, i], L)
    x_1 = res[2]
    y_1 = res[3]
    x_2 = x_1 + L[1] * cos(res[0] + res[1])
    y_2 = y_1 + L[1] * sin(res[0] + res[1])

    # update position of arms and add points to draw circle circle
    line_lower.set_data([x_0, x_1], [y_0, y_1])
    line_upper.set_data([x_1, x_2], [y_1, y_2])
    path_line.set_data(x_e[:i], y_e[:i])
    
    # update angle measurement text
    theta1_text.set_text(f'θ₁: {degrees(res[0]):.1f} degrees')
    theta2_text.set_text(f'θ₂: {degrees(res[1]):.1f} degrees')
    
    ax.set_aspect('equal')
    ax.set_xlim(-1, 2)
    ax.set_ylim(-1, 2)
    ax.set_xlabel('X position')
    ax.set_ylabel('Y position')
    ax.set_title(f'Arm Position (Point {i})')
    return line_lower, line_upper, path_line

# Create the animation
ani = FuncAnimation(fig, animate, frames=columns, init_func=init, repeat=True, interval=10)

# Display the animation
plt.grid()
plt.show()