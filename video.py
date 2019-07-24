'''video ripping controller'''
from abc import ABCMeta, abstractmethod
import threading
import json
from libs.startup_arguments import PROGRAMCONFIGLOCATION
from .ripper_subsystem import RipperSubSystem
from .converter import create_video_converter_row
from .disc_api import apiaccess_video_disc_id
from .data.db_tables import VIDEO_INFO_DB_INFO as INFO_DB
from .data.disc_type import make_disc_type
from .data.events import RipperEvents

class Video(RipperSubSystem, metaclass=ABCMeta):
    '''video ripping controller'''
    def __init__(self, device, config, db, thread_name, disc_type, set_drive_status, thread_run):
        super().__init__(device, config, db, thread_name, set_drive_status, thread_run)
        self._disc_info_lock = threading.Lock()
        self._disc_info_uuid = None
        self._disc_info_label = None
        self._disc_info_sha256 = None
        self._disc_rip_info = None
        self._disc_type = disc_type
        self._db_id = None
        self._set_drive_status = set_drive_status

##########
##CHECKS##
##########
    @abstractmethod
    def _check_disc_information(self):
        '''Will set the UUID and label or it will return False'''

#######################
##DATABASE & API CALL##
#######################
    def _check_db_and_api_for_disc_info(self):
        '''checks the DB and API for the Disc info'''
        uuid = self._disc_info_uuid
        label = self._disc_info_label
        sha256 = self._disc_info_sha256
        disc_type = self._disc_type
        basic_info = {"uuid":uuid, "label":label, "sha256": sha256, "disc_type": disc_type}
        self._db_id = self._db.table_has_row(self._thread_name, INFO_DB["name"], basic_info)
        if self._db_id:
            return_data = self._db.select_by_row(self._thread_name, INFO_DB["name"], self._db_id)
            rip_data_json = return_data['rip_data']
            self._db.update(self._thread_name, INFO_DB["name"], self._db_id,
                            {"ripped":False, "ready_to_convert":False, "ready_to_rename":False,
                             "ready_for_library":False, "completed":False})
            if rip_data_json is not None:
                self._disc_rip_info = make_disc_type(json.loads(rip_data_json))
                return
        else:
            self._db.insert(self._thread_name, INFO_DB["name"], basic_info)
            self._db_id = self._db.table_has_row(self._thread_name, INFO_DB["name"], basic_info)
        rip_list = apiaccess_video_disc_id(uuid, label)
        if isinstance(rip_list, str):
            self._disc_rip_info = make_disc_type(json.loads(rip_list))
            self._db.update(self._thread_name, INFO_DB["name"], self._db_id, {"rip_data":rip_list})

#################
##MAKEMKV CALLS##
#################
    def _call_makemkv_backup(self):
        '''run the makemkv backup function thread safe'''
        temp_location = self._config['locations']['videoripping']
        if temp_location[0] != "/":
            temp_location = PROGRAMCONFIGLOCATION + self._config['locations']['videoripping']
        temp_dir = temp_location + str(self._db_id)
        if isinstance(self._disc_rip_info, list):
            for idx, track in enumerate(self._disc_rip_info):
                if not isinstance(track, bool):
                    self._makemkv_backup_from_disc(temp_dir, idx)
                    if not self._thread_run:
                        return False
        elif self._disc_rip_info is None:
            self._makemkv_backup_from_disc(temp_dir)
        self._set_drive_status("idle")
        self._db.update(self._thread_name, INFO_DB["name"], self._db_id, {"ripped":True})
        return True

    @abstractmethod
    def _makemkv_backup_from_disc(self, temp_dir, index=-1):
        '''Do the mkv Backup from disc'''

#######################
##SEND TO NEXT SYSTEM##
#######################
    def _send_to_next_system(self):
        '''method to send info to the next step in the process'''
        if self._config['converter']['enabled']:
            create_video_converter_row(self._db, self._thread_name, self._db_id,
                                       self._disc_rip_info, self._config['videoripping']['torip'])
            self._db.update(self._thread_name, INFO_DB["name"], self._db_id,
                            {"ready_to_convert":True})
            RipperEvents().converter.set()
        else:
            self._db.update(self._thread_name, INFO_DB["name"], self._db_id,
                            {"ready_to_rename":True})
            RipperEvents().renamer.set()
##########
##Script##
##########
    def run(self):
        '''script to rip video disc'''
        self._set_drive_status("Get disc unique data")
        if not self._check_disc_information():
            return
        if not self._thread_run:
            return
        self._set_drive_status("checking info")
        self._check_db_and_api_for_disc_info()
        if not self._thread_run:
            return
        self._set_drive_status("Ripping Disc")
        if not self._call_makemkv_backup():
            return
        if self._disc_rip_info:
            self._send_to_next_system()
