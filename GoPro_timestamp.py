#GoPro_timestamp.py
#Created by Chris Rillahan
#Last Updated: 1/30/2015
#Written with Python 2.7.2, OpenCV 2.4.8

#This script uses ffprobe to interogate a MP4 file and extract the creation time.
#This information is then used to initiate a counter/clock which is used to put
#the timestamp on each frame of the video.  The videos are samed as *.avi files
#using DIVX compression due to the availability in OpenCV.  The audio is stripped
#out in this script.

import cv2, os, sys, subprocess, shlex, re, time
import datetime as dt
from subprocess import call

#Name of the file
filename = 'Your_GoPro_Video_Here.MP4'

#This function initiates a call to ffprobe which returns a summary report about
#the file of interest.  The returned information is then parsed to extract only
#the creation time of the file.

def creation_time(filename):
    import os, sys, subprocess, shlex, re
    from subprocess import call

    cmnd = ['ffprobe', '-show_format', '-pretty', '-loglevel', 'quiet', filename]
    p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print filename
    out, err =  p.communicate()
    print "==========output=========="
    print out
    if err:
        print "========= error ========"
        print err
    t = out.splitlines()
    time = str(t[14][18:37])
    return time

#Opens the video import and sets parameters
video = cv2.VideoCapture(filename)

#Checks to see if a the video was properly imported
status = video.isOpened()

if status == True: 
    FPS = video.get(cv2.cv.CV_CAP_PROP_FPS)
    width = video.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
    height = video.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
    size = (int(width), int(height))
    total_frames = video.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
    frame_lapse = (1/FPS)*1000

    #Initializes the export video file
    codec = cv2.cv.CV_FOURCC('D','I','V','X')
    video_out = cv2.VideoWriter(filename[:-4] + '.avi', codec, FPS, size, 1)

    #Initializes time origin of the video
    t = creation_time(filename)
    initial = dt.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
    timestamp = initial

    #Initializes the frame counter
    current_frame = 0
    start = time.time()
#    print("Press 'esc' to quit.")
    print('Processing....')
    print(' ')

    #Reads through each frame, calculates the timestamp, places it on the frame and
    #exports the frame to the output video.
    while current_frame < total_frames:
        success, image = video.read()
        elapsed_time = video.get(cv2.cv.CV_CAP_PROP_POS_MSEC)
        current_frame = video.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)
        timestamp = initial + dt.timedelta(microseconds = elapsed_time*1000)
#        print(timestamp)
        cv2.putText(image, 'Date: ' + str(timestamp)[0:10], (50,int(height-150)), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (255, 255, 255), 3)
        cv2.putText(image, 'Time: ' + str(timestamp)[11:-4], (50,int(height-100)), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (255, 255, 255), 3)
        video_out.write(image)
#        cv2.imshow('Video', image)

        k = cv2.waitKey(1)
        if k == 27:
            break
    
    video.release()
    video_out.release()
    cv2.destroyAllWindows()

    #Calculate how long the timestampping took
    duration = (time.time()-float(start))/60

    print("Video has been timestamped")
    print('This video took:' + str(duration) + ' minutes')

else:
    print('Error: Could not load video')
