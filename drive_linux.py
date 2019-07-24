'''Special Linux Drive Functions'''
import fcntl
import os
import time
from subprocess import DEVNULL, PIPE, Popen
from .drive import Drive
from .audiocd_linux import AudioCDLinux
from .video_linux import VideoLinux

class DriveLinux(Drive):
    '''Drive Control ripper program self contained'''

##########
##CHECKS##
##########
    def check_tray(self):
        '''detect_tray reads status of the drive.'''
        with self._drive_lock:
            file_device = os.open(self._device, os.O_RDONLY | os.O_NONBLOCK)
            return_value = fcntl.ioctl(file_device, 0x5326)
            os.close(file_device)
            if return_value == 1: #no disk in tray
                self._set_tray_status("empty")
                self._set_disc_type("none")
                self._set_drive_status("idle")
            elif return_value == 2: #tray open
                self._set_tray_status("open")
                self._set_disc_type("none")
                self._set_drive_status("idle")
            elif return_value == 3: #reading tray
                self._set_tray_status("reading")
                self._set_disc_type("none")
                self._set_drive_status("loading disc")
            elif return_value == 4: #disk in tray
                self._set_tray_status("loaded")
            else:
                self._set_tray_status("unknown")
                self._set_disc_type("none")
                self._set_drive_status("ERROR")

    def _check_disc_type(self, sleep_time=1.0):
        '''Will return the size of the disc'''
        with self._drive_lock:
            if not self._thread_run:
                return False
            if self.get_tray_status() != "loaded":
                self._set_disc_type("None")
                return False
            message = ""
            while message == "":
                process1 = Popen(["udevadm", "info", "--query=all", "--name=" + self._device],
                                 stdout=PIPE, stderr=DEVNULL)
                process2 = Popen(["grep", "ID_FS_TYPE="], stdin=process1.stdout, stdout=PIPE)
                message = process2.communicate()[0].decode('utf-8').replace("\n", "")
                if not self._thread_run:
                    self.unlock_tray()
                    return False
                time.sleep(float(sleep_time))
            file_format = message.rstrip().split("=")[1]
            if file_format == "udf":
                process3 = Popen(["udevadm", "info", "--query=all", "--name=" + self._device],
                                 stdout=PIPE, stderr=DEVNULL)
                process4 = Popen(["grep", "ID_FS_VERSION="], stdin=process3.stdout, stdout=PIPE)
                message = process4.communicate()[0]
                udf_version_str = message.decode('utf-8').rstrip().split("=")[1]
                udf_version_float = float(udf_version_str)
                if udf_version_float == 1.02:
                    self._set_disc_type("dvd")
                elif udf_version_float >= 2.50:
                    self._set_disc_type("bluray")
            else:
                self._set_disc_type("audiocd")
            return True

    # def _check_audio_disc_information(self):
    #     '''Will return if drive is open or it will return a string of the error'''
    #     if self.get_tray_status() != "loaded":
    #         return False
    #     with self._drive_lock:
    #         process = Popen(["cdrdao", "discid", "--device", self._device],
    #                         stdout=PIPE, stderr=DEVNULL)
    #         returned_message = process.communicate()[0].decode('utf-8').rstrip().split("\n")
    #         process.wait()
    #     if not returned_message:
    #         return False
    #     disc_rip_info = {}
    #     for line in returned_message:
    #         disc_rip_info[line.split(":")[0]] = line.split(":")[1]

    #     self._set_disc_rip_info(disc_rip_info)
    #     return True

################
##TRAYCONTROLS##
################
    def open_tray(self):
        '''Send Command to open the tray'''
        with self._drive_lock:
            Popen(["eject", self._device], stdout=DEVNULL, stderr=DEVNULL).wait()

    def close_tray(self):
        '''Send Command to close the tray'''
        with self._drive_lock:
            Popen(["eject", "-t", self._device], stdout=DEVNULL, stderr=DEVNULL).wait()

    def lock_tray(self):
        '''Send Command to lock the tray'''
        with self._drive_lock:
            self._tray_locked = True
            Popen(["eject", "-i1", self._device], stdout=DEVNULL, stderr=DEVNULL).wait()

    def unlock_tray(self):
        '''Send Command to unlock the tray'''
        with self._drive_lock:
            self._tray_locked = False
            Popen(["eject", "-i0", self._device], stdout=DEVNULL, stderr=DEVNULL).wait()

##########
##Script##
##########
    def _audio_rip(self):
        '''script to rip an audio cd'''
        self._ripper = AudioCDLinux(self.get_device(), self._config, self._db,
                                    self._thread.getName(), self._musicbrainz,
                                    self._set_drive_status, self._thread_run)

    def _video_rip(self):
        '''script to rip video disc'''
        self._ripper = VideoLinux(self.get_device(), self._config, self._db,
                                  self._thread.getName(), self._disc_type,
                                  self._set_drive_status, self._thread_run)

###############
#EXTERNAL APPS#
###############
def get_hwinfo_linux():
    '''issues the hwinfo command and passes the info back in a dict'''
    process = Popen(["hwinfo", "--cdrom"], stdout=PIPE, stderr=DEVNULL)
    returned_message = process.communicate()[0]
    devices = returned_message.decode('utf-8').rstrip().split("\n\n")
    device_list = []
    for device in devices:
        device_single_list = {}
        device_lines = device.split("\n")
        for device_line in device_lines[2:]:
            device_line_1 = device_line.lstrip().split(":", 1)
            title = device_line_1[0].lower().replace(" ", "_")
            info = device_line_1[1].strip()
            device_single_list[title] = info
        device_list.append(device_single_list)
    drives = {}
    for hwinfo_item in device_list:
        temp_list = {}
        temp_list['label'] = hwinfo_item["device_files"].split(",")[0]
        temp_list['link'] = hwinfo_item["device_files"].split(",")[0]
        temp_list['model'] = hwinfo_item["model"].replace('"', "")
        temp_list['features'] = hwinfo_item["features"].replace(" ", "").split(",")
        udevadm_process = Popen(["udevadm", "info", "--query=all", "--name=" + temp_list['link']],
                                stdout=PIPE, stderr=DEVNULL)
        grep_process = Popen(["grep", "ID_SERIAL="], stdin=udevadm_process.stdout, stdout=PIPE)
        message = grep_process.communicate()[0]
        uid = message.decode('utf-8').rstrip().split("=")[1].replace("-0:0", "").replace("_", "-")
        drives[uid] = temp_list
    return drives
