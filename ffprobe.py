'''ffprobe system'''
import json
from subprocess import DEVNULL, PIPE, Popen


class FFprobe:
    '''ffprobe system'''

    def __init__(self, ffprob_location, infile):
        prog_args = [ffprob_location,
                     "-v",
                     "quiet",
                     "-print_format",
                     "json",
                     "-show_streams",
                     "-show_chapters",
                     "-show_format",
                     infile
                     ]
        process = Popen(prog_args, stdout=PIPE, stderr=DEVNULL)
        self._info = json.loads(process.communicate()[0].decode('utf-8'))
        process.wait()

    def has_chapters(self):
        '''returns true if file has chapters'''
        if 'chapters' in self._info and self._info['chapters']:
            return True
        return False

    def stream_count(self):
        '''returns the stream count'''
        if 'streams' in self._info and self._info['streams']:
            return len(self._info['streams'])
        return 0

    def get_stream(self, index):
        '''return a stream'''
        if 'streams' in self._info and self._info['streams']:
            return self._info['streams'][int(index)]
        return None

    def stream_type_count(self):
        '''returns the stream types and how many'''
        if 'streams' in self._info and self._info['streams']:
            s_types = {}
            for stream in self._info['streams']:
                _type = stream["codec_type"]
                if _type in s_types:
                    s_types[_type] += 1
                else:
                    s_types[_type] = 1
            return s_types
        return None

    def get_streams_and_types(self):
        '''returns a list of streams and there types'''
        if 'streams' in self._info and self._info['streams']:
            streams = []
            for stream in self._info['streams']:
                streams.append(stream["codec_type"])
            return streams

    def get_video_info(self):
        '''returns the video stream information'''
        videos = []
        if 'streams' in self._info and self._info['streams']:
            for stream in self._info['streams']:
                if stream["codec_type"] == 'video':
                    videos.append(stream)
        return videos

    def get_audio_info(self):
        '''returns the audio stream information'''
        audios = []
        if 'streams' in self._info and self._info['streams']:
            for stream in self._info['streams']:
                if stream["codec_type"] == 'audio':
                    audios.append(stream)
        return audios

    def get_subtitle_info(self):
        '''returns the subtitle stream information'''
        subtitles = []
        if 'streams' in self._info and self._info['streams']:
            for stream in self._info['streams']:
                if stream["codec_type"] == 'subtitle':
                    subtitles.append(stream)
        return subtitles

    def get_format_info(self):
        '''returns the format information'''
        return self._info['format']
