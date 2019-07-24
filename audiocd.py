'''Audio Ripping Feature'''
from abc import ABCMeta, abstractmethod
import json
import discid
from .ripper_subsystem import RipperSubSystem
from .data.db_tables import AUDIO_INFO_DB_INFO as INFO_DB
# from .data.events import RipperEvents

#FORMATS - WAV OGG FLAC MP3 http://opus-codec.org/ http://www.wavpack.com/

#tagging data to be split between cd and track info for saving to the database for use later on
# when converting tag the files if possible at the same time otherwise convert then tag in the
# converter

class AudioCD(RipperSubSystem, metaclass=ABCMeta):
    '''Audio ripping controller'''
    def __init__(self, device, config, db, thread_name, musicbrainz, set_drive_status, thread_run):
        super().__init__(device, config, db, thread_name, set_drive_status, thread_run)
        self._musicbrainz = musicbrainz
        self._disc_id = None
        self._track_count = 0
        self._release_id = None
        self._disc_info = None
        self._db_id = None
        self._ripping_max = 100

##########
##CHECKS##
##########
    def _get_musicbrainz_disc_id(self):
        '''gets the musicbrainz disc id'''
        disc_data = discid.read(self._device)
        self._disc_id = disc_data.id
        self._track_count = disc_data.last_track_num
        if disc_data.first_track_num == 0:
            self._track_count += 1
        elif disc_data.first_track_num == 2:
            self._track_count -= 1

#######################
##DATABASE & API CALL##
#######################
    def _check_db_and_api_for_disc_info(self):
        '''checks the DB and API for the Disc info'''
        basic_info = {"musicbrainz_disc_id":self._disc_id, "track_count":self._track_count}
        self._db_id = self._db.table_has_row(self._thread_name, INFO_DB["name"], basic_info)
        if self._db_id:
            #data in local DB
            return_data = self._db.select_by_row(self._thread_name, INFO_DB["name"], self._db_id)
            self._release_id = return_data['release_id']
            disc_info_json = return_data['disc_data']
            self._db.update(self._thread_name, INFO_DB["name"], self._db_id,
                            {"ripped":False, "ready_to_convert":False, "ready_to_rename":False,
                             "ready_for_library":False, "completed":False})
            if disc_info_json is not None:
                self._disc_info = json.loads(disc_info_json)
                return
        else:
            self._db.insert(self._thread_name, INFO_DB["name"], basic_info)
            self._db_id = self._db.table_has_row(self._thread_name, INFO_DB["name"], basic_info)
        if self._disc_info is None:
            data = self._musicbrainz.get_data_for_discid(self._disc_id)
            if data.get("release-count", 0) == 1:
                self._disc_info = data['release-list'][0]
                self._release_id = self._disc_info['id']
            elif data.get("release-count", 0) > 1:
                self._disc_info = data['release-list']
            else:
                self._disc_info = None

        if self._disc_info is not None:
            data_to_save = {
                "release_id": self._release_id,
                "disc_data": self._disc_info,
            }
            self._db.update(self._thread_name, INFO_DB["name"], self._db_id, data_to_save)


#####################
##DISC RIP COMMANDS##
#####################
    @abstractmethod
    def _rip_disc(self):
        '''command to rip the cd here'''

#######################
##SEND TO NEXT SYSTEM##
#######################
    def _send_to_next_system(self):
        '''method to send info to the next step in the process'''
        # if self._config['converter']['enabled']:
        #     create_video_converter_row(self._db, self._thread_name, self._db_id,
        #                                self._disc_rip_info, self._config['videoripping']['torip'])
        #     self._db.update(self._thread_name, INFO_DB["name"], self._db_id,
        #                     {"ready_to_convert":True})
        #     RipperEvents().converter.set()
        # else:
        #     self._db.update(self._thread_name, INFO_DB["name"], self._db_id,
        #                     {"ready_to_rename":True})
        #     RipperEvents().renamer.set()
##########
##Script##
##########
    def run(self):
        '''script to rip audio cd'''
        self._set_drive_status("Get disc unique data")
        self._get_musicbrainz_disc_id()
        if not self._thread_run:
            return
        self._set_drive_status("checking info")
        self._check_db_and_api_for_disc_info()
        if not self._thread_run:
            return
        self._set_drive_status("Ripping Disc")
        self._rip_disc()
        self._set_drive_status("idle")
        self._db.update(self._thread_name, INFO_DB["name"], self._db_id, {"ripped":True})
        if self._release_id:
            self._send_to_next_system()
