#THIS PROGRAM  OPENS UP MY WEBCAM AND CLOSES IT WHEN Q IS PRESSED, ALSO GRAYSCALES IT

import numpy as np
import cv2

# OpenCV Video capturing variable
cap = cv2.VideoCapture(0)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Grayscale operations on the frame
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Display the resulting frame
    cv2.imshow('frame',gray)
    #set up the "killswitch" key as 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()

