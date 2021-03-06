'''Master Section for the Converter controller'''
import threading
import json
from libs.database import Database
from libs.database.messages import SQLDelete, SQLInsert, SQLSelect, SQLUpdate
from libs.database.where import Where
from config_data import CONFIG
from .data.db_tables import VIDEO_CONVERT_DB_INFO as VIDEO_CONVERT_DB, VIDEO_INFO_DB_INFO as INFO_DB
from .data.disc_type import make_disc_type
from .data.video_track_type import make_track_type
from .converter_video_thread import ConverterVideoThread
from .data.events import RipperEvents


class Converter():
    '''Master Section for the Converter controller'''

    def __init__(self):
        self._thread_name = "Converter"
        self._thread = threading.Thread(target=self.run, args=())
        self._thread.setName(self._thread_name)
        self._thread_run = False
        self._thread_count = 0
        self._tasks_sema = threading.Semaphore(
            CONFIG['plugins']['ripping']['ripper']['converter']['threadcount'].value
        )
        self._tasks = []
        self._list_of_running_ids = []

###########
##GETTERS##
###########
    def get_quick_data(self):
        '''returns the data as dict for html'''
        return [task.get_quick_data() for task in self._tasks]

    def get_data(self):
        '''returns the data as dict for html'''
        return [task.get_data() for task in self._tasks]

    def get_data_ids(self):
        '''returns the data as dict for html'''
        return [task.get_id() for task in self._tasks]

    def get_quick_data_by_id(self, task_id):
        '''returns the data as dict for html'''
        for task in self._tasks:
            if task.get_id() == task_id:
                return task.get_quick_data()
        return None

    def get_data_by_id(self, task_id):
        '''returns the data as dict for html'''
        for task in self._tasks:
            if task.get_id() == task_id:
                return task.get_data()
        return None

    def get_converting_by_id(self, task_id):
        '''returns the data as dict for html'''
        for task in self._tasks:
            if task.get_id() == task_id:
                return task.converting()
        return None
##########
##Thread##
##########

    def start_thread(self):
        '''start the thread'''
        if not self._thread.is_alive():
            self._thread_run = True
            self._thread.start()
            return True
        return False

    def stop_thread(self):
        '''stop the thread'''
        if self._thread.is_alive():
            for task in self._tasks:
                task.stop_thread()
            self._thread_run = False
            self._thread.join()

##########
##Script##
##########
    def run(self):
        ''' Loops through the standard converter function'''
        while self._thread_run:
            self._get_video_tasks()

            if not self._thread_run:
                return
            for task in self._tasks:
                task.start_thread()

            if not self._task_do_loop():
                return

            wake_renamer = False
            if self._clear_video_tasks():
                wake_renamer = True

            if wake_renamer:
                RipperEvents().renamer.set()

            if not self._thread_run:
                return

            RipperEvents().converter.wait()
            RipperEvents().converter.clear()

    def _get_video_tasks(self):
        '''Grab video tasks and append them to the list'''
        msg = SQLSelect(
            VIDEO_CONVERT_DB.name(),
            Where("converted", False)
        )
        Database.call(msg)
        data = []
        if msg.return_data:
            if isinstance(msg.return_data, list):
                data = msg.return_data
            elif isinstance(msg.return_data, dict):
                data.append(msg.return_data)
            for item in data:
                if "v" + item['id'] not in self._list_of_running_ids:
                    item['disc_info'] = make_disc_type(
                        json.loads(item['disc_info']))
                    item['track_info'] = make_track_type(
                        json.loads(item['track_info']))

                    # TEMP HDR SKIPPER
                    if item['track_info'].hdr():
                        continue

                    self._tasks.append(ConverterVideoThread(item,
                                                            self._tasks_sema))
                    self._list_of_running_ids.append("v" + item['id'])

    def _clear_video_tasks(self):
        '''clears the video tasks from the database when done'''
        msg1 = SQLSelect(
            INFO_DB.name(),
            Where("ready_to_convert", True),
            Where("ready_to_rename", False)
        )
        Database.call(msg1)
        discs = [x['id'] for x in msg1.return_data]

        msg2 = SQLSelect(
            VIDEO_CONVERT_DB.name()
        )
        Database.call(msg2)
        wake_renamer = False

        for disc in discs:
            if all([item['converted'] for item in msg2.return_data if item['info_id'] == disc]):
                Database.call(
                    SQLDelete(
                        VIDEO_CONVERT_DB.name(),
                        Where("disc_id", disc)
                    )
                )
                Database.call(
                    SQLUpdate(
                        INFO_DB.name(),
                        Where("id", disc),
                        ready_to_rename=True
                    )
                )
                wake_renamer = True
        return wake_renamer

    def _task_do_loop(self):
        '''loop through the tasks till done'''
        while self._tasks:
            i = 0
            count = len(self._tasks)
            while i < count:
                if self._tasks[i].task_done():
                    del self._tasks[i]
                    count -= 1
                else:
                    i += 1
                if not self._thread_run:
                    for task in self._tasks:
                        task.stop_thread()
                    return False
        return True


def create_video_converter_row(info_id, disc_rip_info, to_rip):
    '''Function to add Video tracks to Convertor DB'''
    folder_name = str(info_id) + "/"
    disc_info = json.dumps(disc_rip_info.make_dict(no_tracks=True))
    for i, track in enumerate(disc_rip_info.tracks()):
        if track.video_type() in to_rip:
            Database.call(
                SQLInsert(
                    VIDEO_CONVERT_DB.name(),
                    info_id=info_id,
                    filename=folder_name + str(i).zfill(2) + ".mkv",
                    disc_info=disc_info,
                    track_info=json.dumps(track.make_dict())
                )
            )

def create_audiocd_converter_row(info_id, disc_rip_info):
    '''Function to add Audio CD tracks to Convertor DB'''
    folder_name = str(info_id) + "/"
    disc_info = json.dumps(disc_rip_info)
    # 'audio_XX.wav'
    #TODO FINISH THIS OFF
