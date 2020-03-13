'''Master Section for the Renamer controller'''
import threading
import json
import os
from libs.startup_arguments import PROGRAMCONFIGLOCATION
from libs.sql import Database
from config_data import CONFIG
from .ffprobe import FFprobe
from .data.events import RipperEvents
from .data.db_tables import VIDEO_INFO_DB_INFO as INFO_DB
from .data.disc_type import make_disc_type


class Renamer():
    '''Master Section for the Renamer controller'''

    def __init__(self):
        self._thread_name = "Renamer"
        self._thread = threading.Thread(target=self.run, args=())
        self._thread.setName(self._thread_name)
        self._thread_run = False
        config = CONFIG['plugins']['ripping']['ripper']['locations']
        self._in_location = config['videoripping'].value
        if self._in_location[0] != "/":
            self._in_location = PROGRAMCONFIGLOCATION
            self._in_location += config['videoripping'].value
        self._out_location = config['videoripping'].value
        if self._out_location[0] != "/":
            self._out_location = PROGRAMCONFIGLOCATION
            self._out_location += config['videoripped'].value
##########
##Thread##
##########

    def start_thread(self):
        '''start the thread'''
        if not self._thread.is_alive():
            self._thread.start()
            return True
        return False

    def stop_thread(self):
        '''stop the thread'''
        if self._thread.is_alive():
            self._thread_run = False
            self._thread.join()

##########
##Script##
##########
    def run(self):
        ''' Loops through the standard renamer function'''
        while self._thread_run:
            self._video_renamer()
            if not self._thread_run:
                return
            RipperEvents().renamer.wait()
            RipperEvents().renamer.clear()

    def _video_renamer(self):
        '''the renamer function for the video files'''
        check = {"ready_to_rename": True}
        return_data = Database.sql().select(
            self._thread_name,
            INFO_DB["name"],
            check
        )
        for item in return_data:
            rip_data = make_disc_type(json.loads(item['rip_data']))
            in_folder = self._in_location + item['id'] + "/"
            out_folder = self._out_location + item['id'] + "/"
            open(out_folder + rip_data.disc_type(), 'a').close()
            try:
                os.mkdir(out_folder)
            except OSError:
                pass
            config = CONFIG['plugins']['ripping']['ripper']
            for i, track in enumerate(rip_data.tracks()):
                if track.video_type() not in config['videoripping']['torip'].value:
                    continue
                in_file = in_folder + str(i).zfill(2) + ".mkv"
                out_file = ""
                if track.video_type() == "movie":
                    out_file += rip_data.name() + " (" + rip_data.year() + ")"
                elif track.video_type() == "tvshow":
                    out_file += rip_data.name() + " - S" + track.season()
                    out_file += "E" + track.episode()
                elif track.video_type() == "trailer":
                    out_file += "trailer - " + rip_data.name() + " - " + track.info()
                elif track.video_type() == "extra":
                    out_file += "extra - " + rip_data.name() + " - " + track.name()
                elif track.video_type() == "other":
                    out_file += "other - " + rip_data.name() + " - " + track.other_type()

                probe_video = FFprobe(config['converter']['ffprobelocation'].value,
                                      in_file).get_video_info()[0]
                if probe_video["height"] > 576:
                    out_file += "." + str(probe_video["height"]) + "p"
                    out_file += ".BluRay"
                else:
                    out_file += ".DVDRip"
                if track.hdr():
                    out_file += ".HDR"
                out_file += ".mkv"
                final_out_file = out_folder + out_file
                os.rename(in_file, final_out_file)

            Database.sql().update(
                self._thread_name,
                INFO_DB["name"],
                item['id'],
                {"ready_for_library": True}
            )
            if not self._thread_run:
                return
