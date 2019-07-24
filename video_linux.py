'''Special Linux Drive Functions'''
import os
import shlex
from subprocess import DEVNULL, PIPE, Popen
import pexpect
from .video import Video

class VideoLinux(Video):
    '''Video Control ripper program self contained'''
##########
##CHECKS##
##########
    def _check_disc_information(self):
        '''Will return if disc is in drive (setting the UUID and label) or it will return False'''
        process = Popen(["blkid", self._device], stdout=PIPE, stderr=DEVNULL)
        returned_message = process.communicate()[0]
        if not returned_message:
            return False
        message = shlex.split(returned_message.decode('utf-8').rstrip().split(": ")[1])
        uuid = message[0].split("=")[1]
        label = message[1].split("=")[1]
        if not self._thread_run:
            return
        # run for a second through mplayer so it will stop any dd I/O errors
        if self._disc_type == "dvd":
            mplayer_process = Popen(["mplayer", "dvd://1", "-dvd-device", self._device, "-endpos",
                                     "1", "-vo", "null", "-ao", "null"], stdout=DEVNULL,
                                    stderr=DEVNULL)
            mplayer_process.wait()
        if not self._thread_run:
            return
        #using DD to read the disc pass it to sha256 to make a unique code for searching by
        dd_process = Popen(["dd", "if=" + self._device, "bs=4M", "count=128", "status=none"],
                           stdout=PIPE, stderr=DEVNULL)
        sha256sum_process = Popen(["sha256sum"], stdin=dd_process.stdout, stdout=PIPE,
                                  stderr=DEVNULL)
        sha256 = sha256sum_process.communicate()[0].decode('utf-8').replace("-", "").rstrip()
        if dd_process.returncode > 0:
            return False
        if not self._thread_run:
            return
        self._disc_info_uuid = uuid
        self._disc_info_label = label
        self._disc_info_sha256 = sha256
        return True

#################
##MAKEMKV CALLS##
#################
    def _makemkv_backup_from_disc(self, temp_dir, index=-1):
        '''Do the mkv Backup from disc'''
        try:
            os.mkdir(temp_dir)
        except OSError:
            pass
        with open(temp_dir + "/info.txt", "w") as text_file:
            string = "UUID: " + self._disc_info_uuid + "\nLabel: " + self._disc_info_label
            text_file.write(string)
        if index == -1:
            index = "all"

        prog_args = [
            "makemkvcon",
            "-r",
            "--minlength=0",
            "--messages=-null",
            "--progress=-stdout",
            "--noscan",
            "mkv",
            "dev:" + self._device,
            str(index),
            temp_dir
        ]
        thread = pexpect.spawn(" ".join(prog_args), encoding='utf-8')

        cpl = thread.compile_pattern_list([
            pexpect.EOF,
            'PRGC:\d+,\d+,"Saving to MKV file"',
            'PRGV:\d+,\d+,\d+',
            'PRGC:\d+,\d+,"Analyzing seamless segments"'
        ])
        update_progress = False
        while True:
            i = thread.expect_list(cpl, timeout=None)
            if i == 0: # EOF
                self._ripping_track = None
                break
            elif i == 1:
                self._ripping_track = int(thread.match.group(0).split(":")[1].split(",")[1])
                update_progress = True
            elif i == 2:
                if update_progress:
                    values = thread.match.group(0).split(":")[1].split(",")
                    self._ripping_file = int(values[0])
                    self._ripping_total = int(values[1])
                    self._ripping_max = int(values[2])
                    self._ripping_file_p = round(float(int(values[0]) / int(values[2]) * 100), 2)
                    self._ripping_total_p = round(float(int(values[1]) / int(values[2]) * 100), 2)
            elif i == 3:
                update_progress = False
                self._ripping_file = self._ripping_max
                self._ripping_file_p = round(float(100), 2)
        try:
            os.remove("wget-log")
            os.remove("wget-log.1")
        except OSError:
            pass
