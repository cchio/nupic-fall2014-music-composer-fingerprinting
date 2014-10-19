#!/bin/usr/python

from midiutil.MidiFile import MIDIFile
import csv
import sys


inverse_fifth_list = [0,7,2,9,4,11,6,1,8,3,10,5]
path_parts = str(sys.argv[1]).split("/")
name = path_parts[len(path_parts)-1].split(".")[0]

def convert_back_note(x):
	return inverse_fifth_list[x]

# Producing prediction midi

MyMIDI = MIDIFile(1)
track = 0
time = 0

MyMIDI.addTrackName(track, time, "Preview Track")
MyMIDI.addTempo(track, time, 120)

with open(str(sys.argv[1])) as csvfile:
	csvfile.next()
	reader = csv.reader(csvfile, delimiter=',')
	for row in reader:
	    if len(row) == 4:
			track = 0
			channel = 0
			number = round(float(row[2]))
			pitch = convert_back_note(int(number)) + 48
			time = float(row[0])
			duration = 2
			volume = 100
			MyMIDI.addNote(track,channel,pitch,time,duration,volume)
	
binfile = open("output_predicted_" + name + ".mid", 'wb')
MyMIDI.writeFile(binfile)
binfile.close()

# Producing actual midi

MyMIDI2 = MIDIFile(1)
track = 0
time = 0

MyMIDI2.addTrackName(track, time, "Preview Track")
MyMIDI2.addTempo(track, time, 120)

with open(str(sys.argv[1])) as csvfile:
	csvfile.next()
	reader = csv.reader(csvfile, delimiter=',')
	for row in reader:
	    if len(row) == 4:
			track = 0
			channel = 0
			number = round(float(row[1]))
			pitch = convert_back_note(int(number)) + 48
			time = float(row[0])
			duration = 2
			volume = 100
			MyMIDI2.addNote(track,channel,pitch,time,duration,volume)
	
binfile = open("output_actual_" + name + ".mid", 'wb')
MyMIDI2.writeFile(binfile)
binfile.close()


# Generating anomaly score

aggr_anomaly = 0
num_rows = 0

with open(str(sys.argv[1])) as csvfile:
	csvfile.next()
	reader = csv.reader(csvfile, delimiter=',')
	for row in reader:
	    if len(row) == 4:
			aggr_anomaly = aggr_anomaly + float(row[3])
			num_rows = num_rows + 1

print str(aggr_anomaly/num_rows)
