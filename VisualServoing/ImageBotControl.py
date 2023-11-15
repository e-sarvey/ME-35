import cv2
import numpy as np
import paho.mqtt.client as mqtt
from mysecrets import MyBroker

# init mqtt client
client = mqtt.Client("EddyElijahLEGO")
client.connect('172.16.9.41')
print('connected to MQTT broker')
def send2Lego(quad):
    direction = {1:'f', 2:'b', 3:'l', 4:'r', None:'s'} # dictionary mapping quadrant to lego car commands
    client.publish('EETopic', str(direction[quad]))

# Function to get quadrant and draw lines and text
def draw_quadrant_lines(image):
    # Get image dimensions
    height, width, _ = image.shape

    # Define quadrant limits
    mid_x = width // 2
    mid_y = height // 2

    # Draw lines indicating quadrant positions
    cv2.line(image, (mid_x, 0), (mid_x, height), (255, 255, 255), 2)
    cv2.line(image, (0, mid_y), (width, mid_y), (255, 255, 255), 2)

    # Add text displaying quadrant numbers
    cv2.putText(image, "1", (mid_x // 2, mid_y // 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(image, "2", (mid_x + mid_x // 2, mid_y // 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(image, "3", (mid_x // 2, mid_y + mid_y // 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(image, "4", (mid_x + mid_x // 2, mid_y + mid_y // 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

# Function to get quadrant of a point in an image
def get_quadrant(x, y, image):
    # Get image dimensions
    height, width, _ = image.shape

    # Define quadrant limits
    mid_x = width // 2
    mid_y = height // 2

    # Check the quadrant of the point
    if x < mid_x and y < mid_y:
        return 1
    elif x >= mid_x and y < mid_y:
        return 2
    elif x < mid_x and y >= mid_y:
        return 3
    elif x >= mid_x and y >= mid_y:
        return 4
    else:
        # Handle the case where the point is exactly on a boundary
        return None

# define a video capture object and start image
vid = cv2.VideoCapture(0)

try:
    prev_quadrant = None  # Variable to track the previous quadrant

    while True:
        # Capture frame-by-frame
        ret, frame = vid.read()

        # Your image processing code here (modify as needed)
        cv2_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        b, g, r = cv2.split(cv2_image)
        green = cv2.subtract(g, r)
        blurred = cv2.GaussianBlur(green, (5, 5), 0)
        thresh = cv2.threshold(blurred, 80, 255, cv2.THRESH_BINARY)[1]
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

        # Initialize variables for the contour with the largest area
        max_contour = None
        max_area = 0

        # Iterate through contours
        for c in cnts:
            area = cv2.contourArea(c)

            # Check if the current contour has a larger area than the previous maximum
            if area > max_area and area > 100:
                max_area = area

                # Compute the center of the contour
                M = cv2.moments(c)
                if M["m00"] != 0:
                    cX = int(M['m10'] / M['m00'])
                    cY = int(M['m01'] / M['m00'])
                else:
                    cX, cY = 0, 0

                # Assign the current contour information to max_contour
                max_contour = [area, cX, cY]

        # Get the quadrant of the center
        quadrant = get_quadrant(max_contour[1], max_contour[2], frame) if max_contour is not None else None

        # Check if the quadrant has changed
        if prev_quadrant != quadrant:
            send2Lego(quadrant)
            print("Quadrant:", quadrant)
            prev_quadrant = quadrant

        # Call the function to draw quadrant lines and text
        draw_quadrant_lines(frame)

        # Plot the center point and coordinates of the contour with the largest area
        if max_contour is not None:
            cv2.circle(frame, (max_contour[1], max_contour[2]), 7, (255, 0, 0), -1)
            cv2.putText(frame, f"({max_contour[1]},{max_contour[2]})", (max_contour[1] - 20, max_contour[2] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # Display the processed frame and thresholded image
        cv2.imshow("Processed Frame", frame)
        cv2.imshow("Thresholded Image", thresh)

        # Break the loop if 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print('keyboard inturrupted!')
finally:
    vid.release()
    cv2.destroyAllWindows()
    client.disconnect()
