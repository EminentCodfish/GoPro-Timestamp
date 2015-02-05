#GoPro_timestamp_with_filewalker.py
#Created by Chris Rillahan
#Last Updated: 1/30/2015
#Written with Python 2.7.2, OpenCV 2.4.8

#This script is the same as the GoPro_timestamp.py except that it adds the
#ability to batch process a series of files.  This script uses the os.walk()
#function to create a list of all the files in a folder.  Each file is then
#iterated through, if the file contains the extension .MP4 then the basic
#timestamp script is executed on the file.


import cv2, time, os, sys, subprocess, shlex, re
import datetime as dt
from subprocess import call

#Creates a command call to ffprobe which returns the files metadata.  The
#metadata is then parsed to return the creation time only.

def creation_time(filename):
    import os, sys, subprocess, shlex, re
    from subprocess import call

    cmnd = ['ffprobe', '-show_format', '-pretty', '-loglevel', 'quiet', filename]
    p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err =  p.communicate()
    print "==========output=========="
    print out
    if err:
        print "========= error ========"
        print err
    t = out.splitlines()
    time = str(t[14][18:37])
    return time

#Directory which contains the video files.
indir = "C:\Your Folder"

#Filewalker function
for root, dirs, filenames in os.walk(indir):
    for f in filenames:
        if f[-4:] == '.MP4':
        
            print('Starting to timestamp: ' + str(f))

            video_filename = f

            #Opens the video import and sets parameters
            video = cv2.VideoCapture(video_filename)

            #Checks to see if a the video was properly imported
            status = video.isOpened()

            if status == True: 
                FPS = video.get(cv2.cv.CV_CAP_PROP_FPS)
                width = video.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
                height = video.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
                size = (int(width), int(height))
                total_frames = video.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
                #frame_lapse = (1/FPS)*1000

                #Initializes the export video file
                codec = cv2.cv.CV_FOURCC('D','I','V','X')
                video_out = cv2.VideoWriter(video_filename[:-4] + '.avi', codec, FPS, size, 1)

                #Initializes time origin of the video
                t = creation_time(video_filename)
                initial = dt.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                timestamp = initial

                #Initializes the frame counter
                current_frame = 0

                start = time.time()

                #iterates through each frame and adds the timestamp before sending
                #the frame to the output file.
                while current_frame < total_frames:
                    success, image = video.read()
                    elapsed_time = video.get(cv2.cv.CV_CAP_PROP_POS_MSEC)
                    current_frame = video.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)
                    timestamp = initial + dt.timedelta(microseconds = elapsed_time*1000)
                    t = timestamp + dt.timedelta(microseconds = -timestamp.microsecond)
                    cv2.putText(image, 'Date: ' + str(timestamp)[0:10], (50,int(height-150)), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (255, 255, 255), 3)
                    cv2.putText(image, 'Time: ' + str(timestamp)[11:-4], (50,int(height-100)), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (255, 255, 255), 3)
                    video_out.write(image)

                    k = cv2.waitKey(1)
                    if k == 27:
                        break
    
                video.release()
                video_out.release()
                cv2.destroyAllWindows()

                duration = (time.time()-float(start))/60

                print("Video has been timestamped")
                print('This video took:' + str(duration) + ' minutes')
            else:
                print('Error: Video failed to load')
    break
