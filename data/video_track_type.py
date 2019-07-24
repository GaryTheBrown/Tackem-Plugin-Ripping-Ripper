'''video track type information'''
from abc import ABCMeta, abstractmethod
import json
from libs import html_parts as ghtml_parts
from . import stream_type
from ..www import html_parts

TYPES = {"dontrip":"ban",
         "movie":"film",
         "tvshow":"tv",
         "trailer":"film",
         "extra":"plus",
         "other":"plus"
        }

class VideoTrackType(metaclass=ABCMeta):
    '''Master Type'''
    def __init__(self, video_type, streams, hdr):
        if video_type in TYPES:
            self._video_type = video_type
        self._streams = streams if isinstance(streams, list) else []
        self._hdr = hdr

    def hdr(self):
        '''return hdr'''
        return self._hdr

    def video_type(self):
        '''returns the type'''
        return self._video_type

    def streams(self):
        '''returns streams'''
        return self._streams

    def _title_html(self, title):
        '''title line for sections'''
        return '<h1 class="text-center">' + title + '</h1>'

    def make_dict(self, super_dict=None, include_streams=True):
        '''returns the tracks'''
        if super_dict is None:
            super_dict = {}
        super_dict["video_type"] = self._video_type
        stream_list = []
        if include_streams:
            for stream in self._streams:
                if stream is None:
                    stream_list.append(None)
                else:
                    stream_list.append(stream.make_dict())
            super_dict["streams"] = stream_list
        super_dict["hdr"] = self._hdr
        return super_dict

    def _change_section_html(self, track):
        '''change section code'''
        html = "<div class=\"onclick topright\" onclick=\"tracktype(" + str(track)
        html += ", 'change');\">(change)</div>"
        return html

    def _make_stream_sections(self, ffprobe):
        '''creates the stream sections'''
        html = ""
        for stream_index, stream_type_code in enumerate(ffprobe.get_streams_and_types()):
            stream_data = ffprobe.get_stream(stream_index)
            if self._streams:
                html += self._streams[stream_index].get_edit_panel(stream_data)
            else:
                temp_stream = stream_type.make_blank_stream_type(stream_index, stream_type_code)
                html += temp_stream.get_edit_panel(stream_data)
        return html_parts.video_panel("Streams", "", html)

    @abstractmethod
    def get_edit_panel(self, ffprobe=None):
        '''returns the edit panel'''

    def _get_edit_panel_bottom(self):
        '''returns the edit panel'''
        html = ""
        html += ghtml_parts.item("track_%%TRACKINDEX%%_hdr", "HDR",
                                 "Is the Track HDR?",
                                 ghtml_parts.checkbox_single("",
                                                             "track_%%TRACKINDEX%%_hdr",
                                                             self._hdr),
                                 True)
        return html

class DONTRIPTrackType(VideoTrackType):
    '''Other Types'''
    def __init__(self, reason):
        super().__init__("dontrip", None, False)
        self._reason = reason

    def reason(self):
        '''return the reason not to rip this track'''
        return self._reason

    def make_dict(self, super_dict=None, include_streams=True):
        '''returns the tracks'''
        if super_dict is None:
            super_dict = {}
        super_dict["reason"] = self._reason
        return super().make_dict(super_dict, include_streams)

    def get_edit_panel(self, ffprobe=None):
        '''returns the edit panel'''
        section_html = self._title_html("Don't Rip")
        section_html += " " + self._change_section_html("%%TRACKINDEX%%")
        section_html += ghtml_parts.hidden("track_%%TRACKINDEX%%_video_type", "dontrip", True)
        section_html += ghtml_parts.item("track_%%TRACKINDEX%%_reason", "Reason",
                                         "Enter the reason not to rip here",
                                         ghtml_parts.input_box("text",
                                                               "track_%%TRACKINDEX%%_reason",
                                                               self._reason),
                                         True)
        return section_html

class MovieTrackType(VideoTrackType):
    '''Movie Type'''
    def __init__(self, streams=None, hdr=False): # tvshow_link=None, tvshow_special_number=None,
        super().__init__("movie", streams, hdr)
    #     self._tvshow_link = tvshow_link
    #     self._tvshow_special_number = tvshow_special_number

    # def tvshow_link(self):
    #     '''return the tv show name for linking'''
    #     return self._tvshow_link

    # def tvshow_special_number(self):
    #     '''return the tv show special number'''
    #     return self._tvshow_special_number

    def make_dict(self, super_dict=None, include_streams=True):
        '''returns the tracks'''
        if super_dict is None:
            super_dict = {}
        return super().make_dict(super_dict, include_streams)

    def get_edit_panel(self, ffprobe=None):
        '''returns the edit panel'''
        section_html = self._title_html("Movie")
        section_html += " " + self._change_section_html("%%TRACKINDEX%%")
        section_html += ghtml_parts.hidden("track_%%TRACKINDEX%%_video_type", "movie", True)
        section_html += super()._get_edit_panel_bottom()
        if ffprobe:
            section_html += self._make_stream_sections(ffprobe)
        return section_html

class TVShowTrackType(VideoTrackType):
    '''TV Show Type'''
    def __init__(self, season, episode, streams=None, hdr=False):
        super().__init__("tvshow", streams, hdr)
        self._season = season
        self._episode = episode

    def season(self):
        '''returns tv show season number'''
        return self._season

    def episode(self):
        '''returns tv show episode number'''
        return self._episode

    def make_dict(self, super_dict=None, include_streams=True):
        '''returns the tracks'''
        if super_dict is None:
            super_dict = {}
        super_dict["season"] = self._season
        super_dict["episode"] = self._episode
        return super().make_dict(super_dict, include_streams)

    def get_edit_panel(self, ffprobe=None):
        '''returns the edit panel'''
        section_html = self._title_html("TV Show Episode")
        section_html += " " + self._change_section_html("%%TRACKINDEX%%")
        section_html += ghtml_parts.hidden("track_%%TRACKINDEX%%_video_type", "tvshow", True)
        section_html += ghtml_parts.item("track_%%TRACKINDEX%%_season", "Season Number",
                                         "Enter the Season Number here",
                                         ghtml_parts.input_box("number",
                                                               "track_%%TRACKINDEX%%_season",
                                                               self._season, minimum=0),
                                         True)
        section_html += ghtml_parts.item("track_%%TRACKINDEX%%_episode", "Episode Number",
                                         "Enter the Episode Number here",
                                         ghtml_parts.input_box("number",
                                                               "track_%%TRACKINDEX%%_episode",
                                                               self._episode, minimum=0),
                                         True)
        section_html += super()._get_edit_panel_bottom()
        if ffprobe:
            section_html += self._make_stream_sections(ffprobe)
        return section_html

class ExtraTrackType(VideoTrackType):
    '''Extra Type'''
    def __init__(self, name, streams=None, hdr=False):
        super().__init__("extra", streams, hdr)
        self._name = name

    def name(self):
        '''returns extra name'''
        return self._name

    def make_dict(self, super_dict=None, include_streams=True):
        '''returns the tracks'''
        if super_dict is None:
            super_dict = {}
        super_dict["name"] = self._name
        return super().make_dict(super_dict, include_streams)

    # def tvshow_link(self):
    #     '''return the tv show name for linking'''
    #     return self._tvshow_link

    # def tvshow_special_number(self):
    #     '''return the tv show special number'''
    #     return self._tvshow_special_number

    def get_edit_panel(self, ffprobe=None):
        '''returns the edit panel'''
        section_html = self._title_html("Extra")
        section_html += " " + self._change_section_html("%%TRACKINDEX%%")
        section_html += ghtml_parts.hidden("track_%%TRACKINDEX%%_video_type", "extra", True)
        section_html += ghtml_parts.item("track_%%TRACKINDEX%%_name", "Name",
                                         "Enter the extra name",
                                         ghtml_parts.input_box("text",
                                                               "track_%%TRACKINDEX%%_name",
                                                               self._name),
                                         True)
        section_html += super()._get_edit_panel_bottom()
        if ffprobe:
            section_html += self._make_stream_sections(ffprobe)
        return section_html

class TrailerTrackType(VideoTrackType):
    '''trailer Type'''
    def __init__(self, info, streams=None, hdr=False):
        super().__init__("trailer", streams, hdr)
        self._info = info

    def info(self):
        '''returns trailers movie info'''
        return self._info

    def make_dict(self, super_dict=None, include_streams=True):
        '''returns the tracks'''
        if super_dict is None:
            super_dict = {}
        super_dict["info"] = self._info
        return super().make_dict(super_dict, include_streams)

    def get_edit_panel(self, ffprobe=None):
        '''returns the edit panel'''
        section_html = self._title_html("Trailer")
        section_html += " " + self._change_section_html("%%TRACKINDEX%%")
        section_html += ghtml_parts.hidden("track_%%TRACKINDEX%%_video_type", "trailer", True)
        section_html += ghtml_parts.item("track_%%TRACKINDEX%%_info", "Information",
                                         "Enter trailer information here",
                                         ghtml_parts.input_box("text",
                                                               "track_%%TRACKINDEX%%_info",
                                                               self._info),
                                         True)
        section_html += super()._get_edit_panel_bottom()
        if ffprobe:
            section_html += self._make_stream_sections(ffprobe)
        return section_html

class OtherTrackType(VideoTrackType):
    '''Other Types'''
    def __init__(self, other_type, streams=None, hdr=False):
        super().__init__("other", streams, hdr)
        self._other_type = other_type

    def other_type(self):
        '''returns other type'''
        return self._other_type

    def make_dict(self, super_dict=None, include_streams=True):
        '''returns the tracks'''
        if super_dict is None:
            super_dict = {}
        super_dict["other_type"] = self._other_type
        return super().make_dict(super_dict, include_streams)

    def get_edit_panel(self, ffprobe=None):
        '''returns the edit panel'''
        section_html = self._title_html("Other")
        section_html += " " + self._change_section_html("%%TRACKINDEX%%")
        section_html += ghtml_parts.hidden("track_%%TRACKINDEX%%_video_type", "other", True)
        section_html += ghtml_parts.item("track_%%TRACKINDEX%%_othertype", "Other Type",
                                         "What is it?",
                                         ghtml_parts.input_box("text",
                                                               "track_%%TRACKINDEX%%_othertype",
                                                               self._other_type),
                                         True)
        section_html += super()._get_edit_panel_bottom()
        if ffprobe:
            section_html += self._make_stream_sections(ffprobe)
        return section_html

def make_track_type(track):
    '''transforms the track returned from the DB or API to the classes above'''
    if isinstance(track, str):
        track = json.loads(track)
    if track is None:
        return None
    streams = []
    if "streams" in track:
        for stream_index, stream in enumerate(track['streams']):
            temp = stream_type.make_stream_type(stream_index, stream)
            streams.append(temp)

    if track['video_type'] == "dontrip":
        return DONTRIPTrackType(track.get('reason', ""))
    elif track['video_type'] == "movie":
        return MovieTrackType(streams=streams, hdr=track.get('hdr', False))
    elif track['video_type'] == "tvshow":
        return TVShowTrackType(track.get('season', ""), track.get('episode', ""), streams=streams,
                               hdr=track.get('hdr', False))
    elif track['video_type'] == "trailer":
        return TrailerTrackType(track.get('info', ""), streams=streams,
                                hdr=track.get('hdr', False))
    elif track['video_type'] == "extra":
        return ExtraTrackType(track.get('name', ""), streams=streams, hdr=track.get('hdr', False))
    elif track['video_type'] == "other":
        return OtherTrackType(track.get('other_type', ""), streams=streams,
                              hdr=track.get('hdr', False))
    return None

def make_blank_track_type(track_type_code):
    '''make the blank track type'''
    if track_type_code.lower() == "dontrip":
        return DONTRIPTrackType("")
    elif track_type_code.lower() == "movie":
        return MovieTrackType()
    elif track_type_code.lower() == "tvshow":
        return TVShowTrackType("", "",)
    elif track_type_code.lower() == "trailer":
        return TrailerTrackType("")
    elif track_type_code.lower() == "extra":
        return ExtraTrackType("")
    elif track_type_code.lower() == "other":
        return OtherTrackType("")
    return None
