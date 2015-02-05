#GoPro_timestamp_with_external_data.py
#Created by Chris Rillahan
#Last Updated: 01/30/2015
#Written with Python 2.7.2, OpenCV 2.4.8

#This script modifies the GoPro_timestamp.py script to add an additional data overlay.
#In this particular example it uses depth data.  This is done by loading the external
#data and saving it into a python dictionary structure.  This script would have to be
#modified if the external datafile structure is different.  When the timestamp is added
#to the video, the external data is retrieved by searching the dictionary for a
#coorsponding time value.  Since this data set contains data every second match the two
#time field is easily done by stripping the milliseconds value off the video time and
#comparing it to the external data time.accept2dyear  If your external data is not recorded
#on a regular time scale like this then some creativity would have to be used to match the
#data fields.

import cv2, time, os, sys, subprocess, shlex, re
import datetime as dt
from subprocess import call

#Names of the two import files
data_name = 'external_data.txt'
video_filename = 'Tow2_T45CE_DMFH3_1.MP4'

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
#    print("Press 'esc' to quit.")
    print('Processing....')
    print(' ')

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
    print('Error: Failed to load video')
