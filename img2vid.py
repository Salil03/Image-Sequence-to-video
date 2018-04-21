#!/usr/local/bin/python3

import cv2
import argparse
import os
import functools
from functools import cmp_to_key
import easygui

#Function to check if string can be cast to int
def isnum (num):
	try:
		int(num)
		return True
	except:
		return False

#Numerically sorts filenames
def image_sort (x,y):
	x = int(x.split(".")[0])
	y = int(y.split(".")[0])
	return x-y

# Construct the argument parser and parse the arguments
frame_rate = int(input("What is the frame rate: "))
exten = input("What is the extension of image files: ")
vis = input("Do you want a preview(true or false): ")
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("-e", "--extension", required=False, default=exten, help="Extension name. default is 'png'.")
arg_parser.add_argument("-o", "--output", required=False, default='output.mp4', help="Output video file.")
arg_parser.add_argument("-d", "--directory", required=False, default='.', help="Specify image directory.")
arg_parser.add_argument("-fps", "--framerate", required=False, default=frame_rate, help="Set the video framerate.")
arg_parser.add_argument("-s", "--sort", required=False, default='numeric', help="Determines the type of file-order sort that will be used.")
arg_parser.add_argument("-t", "--time", required=False, default='none', help="Sets the framerate so that the video length matches the time in seconds.")
arg_parser.add_argument("-v", "--visual", required=False, default=vis, help="If 'true' then will display preview window.")
args = vars(arg_parser.parse_args())

# Arguments
dir_path = args['directory']
ext = args['extension']
output = args['output']
framerate = args['framerate']
sort_type = args['sort']
time = args['time']
visual = args['visual']

#Flips 'visual' to a bool
visual = visual == "true"

#Sets the framerate to argument, or defaults to 10
if not isnum(framerate):
	framerate = 10
else:
	framerate = int(framerate)

#Get the files from directory
images = easygui.fileopenbox(msg="Open all image files",
                             title="Select images", default=("*."+exten), filetypes=None, multiple=True)
#Sort the files found in the directory
if sort_type == "numeric":
	int_name = images[0].split(".")[0]
	if isnum(int_name):
		images = sorted(images, key=cmp_to_key(image_sort))
	else:
		print("Failed to sort numerically, switching to alphabetic sort")
		images.sort()
elif sort_type == "alphabetic":
	images.sort()

#Change framerate to fit the time in seconds if a time has been specified.
#Overrides the -fps arg
if isnum(time):
	framerate = int(len(images) / int(time))
	print("Adjusting framerate to " + str(framerate))

# Determine the width and height from the first image
image_path = os.path.join(dir_path, images[0])
frame = cv2.imread(image_path)

if visual:
	cv2.imshow('video',frame)
regular_size = os.path.getsize(image_path)
height, width, channels = frame.shape

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'x264') # Be sure to use lower case
out = cv2.VideoWriter(output, fourcc, framerate, (width, height))

for n, image in enumerate(images):
	image_path = os.path.join(dir_path, image)
	image_size = os.path.getsize(image_path)
	frame = cv2.imread(image_path)
	out.write(frame) # Write out frame to video
	if visual:
		cv2.imshow('video', frame)

	if (cv2.waitKey(1) & 0xFF) == ord('q'): # Hit `q` to exit
		break
	if n%1 == 0:
		print("Frame " + str(n))

# Release everything if job is finished
out.release()
cv2.destroyAllWindows()

audio = '"' + easygui.fileopenbox(msg="Open audio file", title="Audio", default="*", filetypes=None, multiple=False) + '"'
test = '"' + easygui.filesavebox(msg="Output video", title="Final Video", default=" .mp4", filetypes=None) + '"'
os.system("ffmpeg -loglevel error -i output.mp4 -i " + audio + " -c copy -map 0:v -map 1:a " + test)
os.remove("output.mp4")
print("The output video is " + test)
