#!/usr/bin/env python
# encoding: utf-8
"""
local_db.py

Functions for saving analysis and wave files to local storage
"""

import os
import json
import shutil
import logging

LOG = logging.getLogger(__name__)
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
        LOG.info("Found local database.")
        return
    else:
        LOG.info("Local database not found, creating...")

        os.mkdir(REMIX_FOLDER)
        os.mkdir(AUDIO_FOLDER)
        os.mkdir(ANALYSIS_FOLDER)

        db_file = open(DATABASE, 'wb')
        db_file.close()
        LOG.info("Local database created.")

def check_db(track_md5):
    '''Check the DB and see if the track is in it.'''
    with open(DATABASE, 'r') as db_file:
        for line in db_file:
            if track_md5 == line.strip():
                return True
    return False

def save_to_local(track_md5, audio_file, pyechonest_track):
    '''Save a track to the db.'''
    with open(DATABASE, 'a') as db_file:
        db_file.write(track_md5 + '\n')

    save_audio_to_local(track_md5, audio_file)
    save_analysis_to_local(track_md5, pyechonest_track)

def save_audio_to_local(track_md5, audio_file):
    '''Copy the uncompressed audio file to the db.'''
    target_file = AUDIO_FOLDER + os.path.sep + track_md5 + '.wav'
    shutil.copyfile(audio_file, target_file)

def save_analysis_to_local(track_md5, pyechonest_track):
    '''Save the pyechonest track dict as json to the db.'''
    target_file = ANALYSIS_FOLDER + os.path.sep + track_md5 + '.analysis'
    with open(target_file, 'wb') as db_file:
        json.dump(pyechonest_track.__dict__, db_file)

def get_audio_file(track_md5):
    '''Get an audio file from the db.'''
    target_file = AUDIO_FOLDER + os.path.sep + track_md5 + '.wav'
    return target_file

def get_analysis_file(track_md5):
    '''Get an analysis file from the db.'''
    target_file = ANALYSIS_FOLDER + os.path.sep + track_md5 + '.analysis'
    return target_file
