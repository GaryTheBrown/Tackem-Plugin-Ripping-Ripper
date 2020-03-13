'''Master Section for the VideoLabeler controller'''
import json
from libs.sql import Database
from config_data import CONFIG
from .converter import create_video_converter_row
from .data.events import RipperEvents
from .data.db_tables import VIDEO_INFO_DB_INFO as INFO_DB
from .data.disc_type import DiscType


class VideoLabeler():
    '''Master Section for the Drive controller'''


##############
##HTML STUFF##
##############

    def get_count(self, thread_name):
        '''returns the data as dict for html'''
        dict_of_values = {"ripped": True,
                          "ready_to_convert": False, "ready_to_rename": False}
        return Database.sql().count_where(
            thread_name,
            INFO_DB["name"],
            dict_of_values
        )

    def get_ids(self, thread_name):
        '''returns the data as dict for html'''
        dict_of_values = {"ripped": True,
                          "ready_to_convert": False, "ready_to_rename": False}
        return_values = ["id"]
        return_data = Database.sql().select(
            thread_name,
            INFO_DB["name"],
            dict_of_values,
            return_values
        )
        return [item['id'] for item in return_data]

    def get_data(self, thread_name):
        '''returns the data as dict for html'''
        dict_of_values = {"ripped": True,
                          "ready_to_convert": False, "ready_to_rename": False}
        return_values = ["id", "uuid", "label", "disc_type", "rip_data"]
        return Database.sql().select(
            thread_name,
            INFO_DB["name"],
            dict_of_values,
            return_values
        )

    def get_data_by_id(self, thread_name, db_id):
        '''returns the data by id as dict for html'''
        data = Database.sql().select_by_row(
            thread_name, INFO_DB["name"], db_id)
        if data is False:
            return False
        if data["ripped"] is False:
            return False
        if data["ready_to_convert"] is True:
            return False
        if data["ready_to_rename"] is True:
            return False
        return data

    def set_data(self, thread_name, db_id, data, finished=False):
        '''Sets Data Back in the Database'''
        if issubclass(type(data), DiscType):
            rip_data = json.dumps(data.make_dict())
        elif isinstance(data, dict):
            rip_data = json.dumps(data)
        else:
            return
        dict_for_db = {"rip_data": rip_data}
        config = CONFIG['plugins']['ripping']['ripper']
        if finished:
            if config['converter']['enabled'].value:
                create_video_converter_row(
                    thread_name,
                    db_id,
                    data,
                    config['videoripping']['torip'].value
                )
                dict_for_db["ready_to_convert"] = True
            else:
                dict_for_db["ready_to_rename"] = True

        Database.sql().update(thread_name, INFO_DB["name"], db_id, dict_for_db)

        if finished:
            if config['converter']['enabled'].value:
                RipperEvents().converter.set()
            else:
                RipperEvents().renamer.set()

    def clear_rip_data(self, thread_name, db_id):
        '''Clears the rip data from the database'''
        Database.sql().update(
            thread_name, INFO_DB["name"], db_id, {"rip_data": None})

    def clear_rip_track_data(self, thread_name, db_id, track_id):
        '''Clears the rip data from the database'''
        data = Database.sql().select_by_row(
            thread_name,
            INFO_DB["name"],
            db_id,
            ["rip_data"]
        )
        rip_data = json.loads(data['rip_data'])
        if isinstance(rip_data, dict):
            if "tracks" in rip_data and isinstance(rip_data["tracks"], list):
                if len(rip_data["tracks"]) >= track_id:
                    rip_data["tracks"][track_id] = None
                    to_save = json.dumps(rip_data)
                    Database.sql().update(
                        thread_name,
                        INFO_DB["name"],
                        db_id,
                        {"rip_data": to_save}
                    )
