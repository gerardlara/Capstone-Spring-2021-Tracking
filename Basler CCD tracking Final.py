# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import argparse
import imutils
import time
import cv2
import numpy as np
import pandas as pd
from pypylon import pylon


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", type=str,
	help="path to input video file")
ap.add_argument("-t", "--tracker", type=str, default="KCF",
	help="OpenCV object tracker type")
args = vars(ap.parse_args())


# extract the OpenCV version info
(major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
print(cv2.__version__)
# function to create our object tracker

if int(major_ver) < 4 and int(minor_ver) < 3:
        tracker = cv2.cv2.Tracker_create(tracker_type)


# otherwise, for OpenCV 3.3 OR NEWER, we need to explicity call the
# appropriate object tracker constructor:

else:
	tracker = cv2.TrackerKCF_create()

# initialize the bounding box coordinates of the object we are going
# to track

initBB = None


# if a video path was not supplied, grab the reference to the camera
if not args.get("video", False):
    print("[INFO] starting video stream...")
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
    time.sleep(1.0)

# otherwise, grab a reference to the video file
else:
    vs = cv2.VideoCapture(args["video"])


#Here's the image converter
converter = pylon.ImageFormatConverter()
converter.OutputPixelFormat = pylon.PixelType_BGR8packed
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

# initialize the FPS throughput estimator
fps = None

#Initialize Coordinate recording, up to 100 points
MAXCOORDS = 100
xf = np.zeros(MAXCOORDS)
yf = np.zeros(MAXCOORDS)
u = 0


# loop over frames from the video stream

while True:

	#then if from pylon
    ####Use the camera to grab results

    grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)


    #Here, if the results are working, convert the grabbed image into new format

    if grabResult.GrabSucceeded():
        # Access the image data
        image = converter.Convert(grabResult)
        img = image.GetArray()
        frame = img[1] if args.get("video", False) else img
	    # check to see if we have reached the end of the stream
        if frame is None:
            break

	    # resize the frame (so we can process it faster) and grab the
	    # frame dimensions
        frame = imutils.resize(frame, width=500)
        (H, W) = frame.shape[:2]


	    # check to see if we are currently tracking an object
        if initBB is not None:
		    # grab the new bounding box coordinates of the object
            (success, box) = tracker.update(frame)

		    # check to see if the tracking was a success
            if success:
                (x, y, w, h) = [int(v) for v in box]
                cv2.rectangle(frame, (x, y), (x + w, y + h),
				    (145, 77, 80), 2)
                PositionTuple = (x + w/ 2, y + h /2)
            

		    # update the FPS counter
            fps.update()
            fps.stop()


		    # initialize the set of information we'll be displaying on
		    # the frame
            Position = (x + w/ 2, y + h /2)
            info = [
            ("Position", PositionTuple),
			("Tracker", args["tracker"]),
			("Success", "Yes" if success else "No"),
			("FPS", "{:.2f}".format(fps.fps()))
		    ]
            xposition, yposition = PositionTuple

            #MAIN LOOP FOR STORING COORDS

            if u < MAXCOORDS:
                xf[u] = xposition
                yf[u] = yposition
                u= u+1


			# loop over the info tuples and draw them on our frame
            for (i, (k, v)) in enumerate(info):
                text = "{}: {}".format(k, v)
                cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
				    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    else:
        print("Check Camera Settings")
        break

	# show the output frame
    cv2.imshow("Frame", frame)

    key = cv2.waitKey(1) & 0xFF
	# if the 's' key is selected, we are going to "select" a bounding
	# box to track
    if key == ord("s"):
		# select the bounding box of the object we want to track (make
		# sure you press ENTER or SPACE after selecting the ROI)
        initBB = cv2.selectROI("Frame", frame, fromCenter=False, showCrosshair=True)
		# start OpenCV object tracker using the supplied bounding box
		# coordinates, then start the FPS throughput estimator as well
        tracker.init(frame, initBB)
        fps = FPS().start()


	# if the `q` key was pressed, break from the loop
    elif key == ord("x"):
        break

cv2.destroyAllWindows()


#Showing DataFrame made from stored points

df = pd.DataFrame({'X-Position':xf, 'Y-Position':yf})
print(df)
df.to_csv('POSITION.csv', index= False)
