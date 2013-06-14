#!/usr/bin/env python
# encoding: utf=8

"""
videolizer.py

Sync up some video sequences to a song.
Created by Tristan Jehan.
"""
import echonest.remix.audio as aud
from sys import stdout
import subprocess
import random
import shutil
import glob
import sys
import os

VIDEO_FOLDER = 'videos'
IMAGE_FOLDER = 'images'
AUDIO_FOLDER = 'audio'
AUDIO_EXAMPLE = '../music/Tracky_Birthday-Newish_Disco.mp3'
TMP_FOLDER = IMAGE_FOLDER+'/tmp'
VIDEO_CSV = 'video.csv'
EXTENSION = '.mp4'
TMP_CSV = 'tmp.csv'
NUM_BEATS_RANGE = (16,32)
EPSILON = 10e-9
BITRATE = 1000000
FPS = 30

def display_in_place(line):
    stdout.write('\r%s' % line)
    stdout.flush()

def time_to_frame(time):
    return int(time * FPS)

def frame_to_time(frame):
    return float(frame) / float(FPS)

def process_videos(folder, csv_file):
    files = glob.glob(folder+'/*'+EXTENSION)
    print "Converting videos to images..."
    for f in files:
        print "> %s..." % f
        convert_video_to_images(f, IMAGE_FOLDER)
    print "Extracting audio from video..."
    for f in files:
        print "> %s..." % f
        convert_video_to_audio(f)
    print "Analyzing video beats..."
    if os.path.exists(TMP_CSV):
        os.remove(TMP_CSV)
    for f in files:
        print "> %s..." % f
        analyze_video_beats(f, TMP_CSV)
    os.rename(TMP_CSV, csv_file)

def video_to_audio(video):
    if not os.path.exists(AUDIO_FOLDER):
        os.makedirs(AUDIO_FOLDER)
    ext = os.path.splitext(video)[1]
    audio = video.replace(ext,'.m4a').replace(VIDEO_FOLDER, AUDIO_FOLDER)
    return audio

def convert_video_to_images(video, output):
    ext = os.path.splitext(video)[1]
    name = os.path.basename(video.replace(ext,'')).split('.')[0]
    folder = output+'/'+name
    if not os.path.exists(folder):
        os.makedirs(folder)
        command = 'en-ffmpeg -loglevel panic -i \"%s\" -r %d -f image2 \"%s/%%05d.png\"' % (video, FPS, folder)
        cmd = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        cmd.wait()

def convert_video_to_audio(video):
    audio = video_to_audio(video)
    if not os.path.exists(audio):
        command = 'en-ffmpeg -loglevel panic -y -i \"%s\" -vn -acodec copy \"%s\"' % (video, audio)
        cmd = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        cmd.wait()

def analyze_video_beats(video, csv_file):
    audio = video_to_audio(video)
    track = aud.LocalAudioFile(audio, verbose=True)
    beats = track.analysis.beats
    mini = 0
    maxi = sys.maxint
    l = video.split('.')
    if len(l) > 3:
        if l[-3].isdigit() and int(l[-3]) is not 0:
            mini = int(l[-3])
        if l[-2].isdigit() and int(l[-2]) is not 0:
            maxi = int(l[-2])
    line = video
    for beat in beats:
        if mini < beat.start and beat.start < maxi:
            line = line+',%.5f' % beat.start
    fid = open(csv_file, 'a')
    fid.write(line+'\n')
    fid.close()

def crop_audio(audio_file, beats):
    ext = os.path.splitext(audio_file)[1]
    name = os.path.basename(audio_file)
    output = AUDIO_FOLDER+'/'+name.replace(ext,'.cropped'+ext)
    if not os.path.exists(output):
        print "Cropping audio to available beats..."
        duration = float(beats[-1].start) - float(beats[0].start)
        command = 'en-ffmpeg -loglevel panic -y -ss %f -t %f -i \"%s\" \"%s\"' % (float(beats[0].start), duration, audio_file, output)
        cmd = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        cmd.wait()
    return output

def combine_audio_and_images(audio_file, images_folder, output):
    print "Making final video out of image sequences..."
    tmp_video = VIDEO_FOLDER+'/tmp'+EXTENSION
    command = 'en-ffmpeg -loglevel panic -f image2 -r %d -i \"%s/%%05d.png\" -b %d \"%s\"' % (FPS, images_folder, BITRATE, tmp_video)
    cmd = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    cmd.wait()
    print "Combining final video with cropped audio..."
    command = 'en-ffmpeg -loglevel panic -vcodec copy -y -i \"%s\" -i \"%s\" \"%s\"' % (audio_file, tmp_video, output)
    cmd = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    cmd.wait()
    os.remove(tmp_video)

def select_sequences(number_beats, data):
    sequences = []
    count_beats = 0
    keys = data.keys()
    while count_beats < number_beats:
        video = random.choice(keys)
        nbeats = random.randint(NUM_BEATS_RANGE[0], NUM_BEATS_RANGE[1])
        vbeats = data[video]
        if nbeats >= len(vbeats):
            nbeats = len(vbeats)
        if count_beats + nbeats > number_beats:
            nbeats = number_beats - count_beats
        start = random.randint(0, len(vbeats)-nbeats-1)
        count_beats += nbeats
        sequences.append((video, start, nbeats))
    return sequences

def resample_sequences(source_beats, sequences, data, tmp_folder):
    print "Building new video as a sequence of images..."
    audio_beats = [float(b.start) for b in source_beats]
    jitter = 0
    counter_beats = 0
    counter_images = 0
    for seq in sequences:
        ext = os.path.splitext(seq[0])[1]
        name = os.path.basename(seq[0].replace(ext,'')).split('.')[0]
        src_folder = IMAGE_FOLDER+'/'+name
        video_beats = data[seq[0]]
        video_time = float(video_beats[seq[1]])
        audio_time = float(audio_beats[counter_beats])
        for beats in zip(audio_beats[counter_beats+1:counter_beats+seq[2]+1], video_beats[seq[1]+1:seq[1]+seq[2]+1]):
            audio_beat_dur = beats[0] - audio_time
            video_beat_dur = beats[1] - video_time    
            rate = audio_beat_dur / video_beat_dur
            num_frames_float = video_beat_dur * rate * FPS
            num_frames = int(num_frames_float)
            jitter += num_frames_float - num_frames
            if jitter >= 1-EPSILON:
                num_frames += int(jitter)
                jitter -= int(jitter)
            for i in range(0, num_frames):
                counter_images += 1
                src = '%s/%05d.png' % (src_folder, time_to_frame(video_time + frame_to_time(i/rate)))
                dst =  '%s/%05d.png' % (tmp_folder, counter_images)
                display_in_place('Copying %s to %s' % (src, dst))
                shutil.copyfile(src, dst)
            video_time = beats[1] - frame_to_time(jitter)
            audio_time = beats[0]
        counter_beats += seq[2]
    print

def process_csv(csv_file):
    data = {}
    fid = open(csv_file,'r')
    for line in fid:
        l = line.strip().split(',')
        data[l[0]] = [float(v) for v in l[1:]]
    fid.close()
    return data

def videolize(file_in, file_ou):
    if not os.path.exists(VIDEO_CSV):
        process_videos(VIDEO_FOLDER, VIDEO_CSV)
    data = process_csv(VIDEO_CSV)
    track = aud.LocalAudioFile(file_in, verbose=True)
    beats = track.analysis.beats
    if os.path.exists(TMP_FOLDER):
        shutil.rmtree(TMP_FOLDER)
    os.makedirs(TMP_FOLDER)
    sequences = select_sequences(len(beats)-1, data)
    resample_sequences(beats, sequences, data, TMP_FOLDER)
    file_cropped = crop_audio(file_in, beats)
    combine_audio_and_images(file_cropped, TMP_FOLDER, file_ou)
    shutil.rmtree(TMP_FOLDER)

def main():
    usage = "usage:\tpython %s <file.mp3>\ntry:\tpython %s %s\
    \nnote:\tvideo filename format is name.<time_start>.<time_end>.mp4\n\
    \twith <time_start> and <time_end> in seconds, where 0 means ignore" % (sys.argv[0], sys.argv[0], AUDIO_EXAMPLE)
    if len(sys.argv) < 2:
        print usage
        return -1
    file_in = sys.argv[1]
    ext = os.path.splitext(file_in)[1]
    name = os.path.basename(file_in.replace(ext,''))
    file_ou = name+EXTENSION
    videolize(file_in, file_ou)

if __name__ == "__main__":
    try:
        main()
    except Exception, e:
        print e
