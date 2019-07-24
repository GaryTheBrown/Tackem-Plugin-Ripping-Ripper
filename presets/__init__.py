'''functions to load presets'''
import os
import json
import glob
from libs.config_option import ConfigOption

_DIR = os.path.dirname(__file__)
_VIDEO_PRESET_FILES = glob.glob(_DIR + "/video/*.json")
_VIDEO_PRESET_FILES_DATA = [json.loads(str(open(x).read())) for x in _VIDEO_PRESET_FILES]

def video_presets_config_options():
    '''returns a list of 2 letter codes'''
    return [ConfigOption(x['filename'], x['label']) for x in _VIDEO_PRESET_FILES_DATA]

def get_video_preset_command(filename):
    '''returns the command from the video preset list'''
    for item in _VIDEO_PRESET_FILES_DATA:
        if item['filename'] == filename:
            return item['command']
    return ""
