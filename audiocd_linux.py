'''Audio Ripping Feature'''
import os
import pexpect
from libs.startup_arguments import PROGRAMCONFIGLOCATION
from .audiocd import AudioCD

#FORMATS - WAV OGG FLAC MP3 http://opus-codec.org/ http://www.wavpack.com/

class AudioCDLinux(AudioCD):
    '''Audio CD ripping controller'''

#####################
##DISC RIP COMMANDS##
#####################
    def _rip_disc(self):
        '''command to rip the cd here'''

        temp_location = self._config['locations']['audioripping']
        if temp_location[0] != "/":
            temp_location = PROGRAMCONFIGLOCATION + self._config['locations']['audioripping']
        temp_dir = temp_location + str(self._db_id)
        try:
            os.mkdir(temp_dir)
        except OSError:
            pass

        prog_args = [
            "cdda2wav",
            "-paranoia",
            "-B",
            "-D",
            self._device,
        ]

        thread = pexpect.spawn(" ".join(prog_args), encoding='utf-8', cwd=temp_dir)

        cpl = thread.compile_pattern_list([
            pexpect.EOF,
            '\d+%'
        ])
        self._ripping_track = 0
        while True:
            i = thread.expect_list(cpl, timeout=None)
            if i == 0: # EOF
                _ripping_track = None
                break
            elif i == 1:
                value = int(thread.match.group(0).rstrip().replace("%", ""))
                if value == 0 and next_track:
                    self._ripping_track += 1
                    next_track = False
                else:
                    next_track = True
                total = round(((self._ripping_track - 1) * 100 + value) / self._track_count, 2)
                self._ripping_file_p = self._ripping_file = value
                self._ripping_total_p = self._ripping_total = total
