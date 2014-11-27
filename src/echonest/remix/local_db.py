#!/usr/bin/env python
# encoding: utf-8
"""
local_db.py

Functions for saving analysis and wave files to local storage
"""

import sys
import os
import json
import shutil


HOME = os.path.expanduser("~")
REMIX_PATH = '.remix-db'
REMIX_FOLDER = HOME + os.path.sep + REMIX_PATH
AUDIO_FOLDER = REMIX_FOLDER + os.path.sep + 'audio'
ANALYSIS_FOLDER = REMIX_FOLDER + os.path.sep + 'analysis'
DATABASE = REMIX_FOLDER + os.path.sep + 'database.db'

def check_and_create_local_db():
    '''If the local db does not exist, create it.'''
    home_dir = os.listdir(HOME)
    if REMIX_PATH in home_dir:
        print >> sys.stderr, "Found local database."
        return
    else:
        print >> sys.stderr, "Local database not found, creating..."

        os.mkdir(REMIX_FOLDER)
        os.mkdir(AUDIO_FOLDER)
        os.mkdir(ANALYSIS_FOLDER)

        f = open(DATABASE, 'wb')
        f.close()
        print >> sys.stderr, "Local database created."

def check_db(track_md5):
    # read the db, and see if the md5 is in it
    with open(DATABASE, 'r') as f:
        for line in f:
            if track_md5 == line.strip():
                return True
    return False

def save_to_local(track_md5, audio_file, pyechonest_track):
    # write to the file
    with open(DATABASE, 'a') as f:
        f.write(track_md5 + '\n')

    save_audio_to_local(track_md5, audio_file)
    save_analysis_to_local(track_md5, pyechonest_track)

def save_audio_to_local(track_md5, audio_file):
    # copy the audio file to the proper path, with the proper name
    # This should be the straight-up file path
    target_file = AUDIO_FOLDER + os.path.sep + track_md5 + '.wav'
    shutil.copyfile(audio_file, target_file)

def save_analysis_to_local(track_md5, pyechonest_track):
    # We get a pyechonest track object, and just dump the json of the dict
    target_file = ANALYSIS_FOLDER + os.path.sep + track_md5 + '.analysis'
    with open(target_file, 'wb') as f:
        json.dump(pyechonest_track.__dict__, f)

def get_audio_file(track_md5):
    target_file = AUDIO_FOLDER + os.path.sep + track_md5 + '.wav'
    return target_file

def get_analysis_file(track_md5):
    target_file = ANALYSIS_FOLDER + os.path.sep + track_md5 + '.analysis'
    return target_file
        
        

