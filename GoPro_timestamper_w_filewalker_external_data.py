#GoPro_timestamp with filewalker and external data.py
#Created by Chris Rillahan
#Last Updated: 01/30/2015
#Written with Python 2.7.2, OpenCV 2.4.8

#This script contains the basic timestamp with the filewalker and external data
#overlay.

import cv2, time, os, sys, subprocess, shlex, re
import datetime as dt
from subprocess import call

data_name = 'External_data.txt'
indir = "C:\Your Folder\"

#This function initiates a call to ffprobe which returns a summary report about
#the file of interest.  The returned information is then parsed to extract only
#the creation time of the file.

def creation_time(filename):
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

#Importing and parsing of the external data file
try:
    import_file = open(data_name, 'r')
except:
    print('Failed to import the external data file')
    sys.exit()
    
print('Data file successfully loaded.')

time_rec = []
pressure = []
depth = []
time_depth = {}

for lines in import_file.read().splitlines():
    if lines != '':
        data = lines.split()
        time_rec.append(dt.datetime.strptime((data[0] + ' ' + data[1] + '000'), "%d-%b-%Y %H:%M:%S.%f"))
        pressure.append(float(data[2]))
        depth.append(float(data[3]))

dt_dic = dict(zip(time_rec, depth))

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
                frame_lapse = (1/FPS)*1000

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

                while current_frame < total_frames:
                    success, image = video.read()
                    elapsed_time = video.get(cv2.cv.CV_CAP_PROP_POS_MSEC)
                    current_frame = video.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)
                    timestamp = initial + dt.timedelta(microseconds = elapsed_time*1000)
                    t = timestamp + dt.timedelta(microseconds = -timestamp.microsecond)
                    depth_value = dt_dic[t]
                    cv2.putText(image, 'Date: ' + str(timestamp)[0:10], (50,int(height-150)), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (255, 255, 255), 3)
                    cv2.putText(image, 'Time: ' + str(timestamp)[11:-4], (50,int(height-100)), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (255, 255, 255), 3)
                    cv2.putText(image, 'Depth: '+ str(depth_value)[0:-3], (50,int(height-50)),cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (255, 255, 255), 3)
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
