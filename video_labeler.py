'''Master Section for the VideoLabeler controller'''
import json
from libs.database import Database
from libs.database.messages import SQLSelect, SQLTableCountWhere, SQLUpdate
from libs.database.where import Where
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

    def get_count(self):
        '''returns the data as dict for html'''
        msg = SQLTableCountWhere(
            INFO_DB.name(),
            Where("ripped", True),
            Where("ready_to_convert", False),
            Where("ready_to_rename", False)
        )
        Database.call(msg)
        return msg.return_data['count(*)']

    def get_ids(self):
        '''returns the data as dict for html'''
        msg = SQLSelect(
            INFO_DB.name(),
            Where("ripped", True),
            Where("ready_to_convert", False),
            Where("ready_to_rename", False)
        )
        Database.call(msg)
        return [item['id'] for item in msg.return_data]

    def get_data(self):
        '''returns the data as dict for html'''
        msg = SQLSelect(
            INFO_DB.name(),
            Where("ripped", True),
            Where("ready_to_convert", False),
            Where("ready_to_rename", False)
        )
        Database.call(msg)
        return msg.return_data

    def get_data_by_id(self, db_id):
        '''returns the data by id as dict for html'''
        msg = SQLSelect(
            INFO_DB.name(),
            Where("id", db_id)
        )
        Database.call(msg)
        if not msg.return_data:
            return False
        if msg.return_data["ripped"] is False:
            return False
        if msg.return_data["ready_to_convert"] is True:
            return False
        if msg.return_data["ready_to_rename"] is True:
            return False
        return msg.return_data

    def set_data(self, db_id, data, finished=False):
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
                    db_id,
                    data,
                    config['videoripping']['torip'].value
                )
                dict_for_db["ready_to_convert"] = True
            else:
                dict_for_db["ready_to_rename"] = True
        Database.call(
            SQLUpdate(
                INFO_DB.name(),
                Where("id", db_id),
                **dict_for_db
            )
        )
        if finished:
            if config['converter']['enabled'].value:
                RipperEvents().converter.set()
            else:
                RipperEvents().renamer.set()

    def clear_rip_data(self, db_id):
        '''Clears the rip data from the database'''
        Database.call(
            SQLUpdate(
                INFO_DB.name(),
                Where("id", db_id),
                rip_data=None
            )
        )

    def clear_rip_track_data(self, db_id, track_id):
        '''Clears the rip data from the database'''
        msg1 = SQLSelect(
            INFO_DB.name(),
            Where("id", db_id),
        )
        Database.call(msg1)
        rip_data = json.loads(msg1.return_data['rip_data'])
        if isinstance(rip_data, dict) and "tracks" in rip_data \
            and isinstance(rip_data["tracks"], list) and len(rip_data["tracks"]) >= track_id:
            rip_data["tracks"][track_id] = None
            to_save = json.dumps(rip_data)
            Database.call(
                SQLUpdate(
                    INFO_DB.name(),
                    Where("id", db_id),
                    rip_data=to_save
                )
            )
