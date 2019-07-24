'''Ripper Linux init'''
import sys
import platform
import pathlib
import threading
from configobj import ConfigObj
from validate import Validator
from libs.startup_arguments import PROGRAMCONFIGLOCATION
from libs.plugin_base import PluginBaseClass
from libs.config_list import ConfigList
from libs.config_object import ConfigObject
from libs.config_option import ConfigOption
from libs.config_rules import ConfigRules
from libs.program_checker import check_for_required_programs
from libs.data.languages import Languages
from libs.data.audio_format_options import OPTIONS as audio_format_options
from . import www
from .data import db_tables
from .data.events import RipperEvents
from .drive_linux import DriveLinux, get_hwinfo_linux
from .video_labeler import VideoLabeler
from .converter import Converter
from .renamer import Renamer
from .presets import video_presets_config_options

SETTINGS = {
    'single_instance':True,
    'webui':True,
    'api':True,
    'type':'ripping',
    'platform': ['Linux']#, 'Darwin', 'Windows']
}
DRIVES = {}

LINUX_PROGRAMS = ["hwinfo", "makemkvcon", "java", "ccextractor", "ffmpeg", "ffprobe", "mplayer",
                  "eject", "lsblk", "hwinfo", "blkid"]

if platform.system() == 'Linux':
    if check_for_required_programs(LINUX_PROGRAMS, output=False):
        DRIVES = get_hwinfo_linux()

def check_enabled():
    '''plugin check for if plugin should be enabled'''
    if platform.system() == 'Linux':
        if not check_for_required_programs(LINUX_PROGRAMS, "Ripper"):
            return False
    return bool(DRIVES)

CONFIG = ConfigList("ripper", plugin=sys.modules[__name__], objects=[
    ConfigObject("enabled", "Enabled", "boolean", default=False, input_type="switch",
                 script=True),
    ConfigList("locations", "Folder Location", objects=[
        ConfigObject("videoripping", "Video Ripping Location", "string", default="videoripping/",
                     help_text="""
Where do you want to store video discs while ripping them?"""),
        ConfigObject("videoripped", "Video Ripped Location", "string", default="videoripped/",
                     help_text="""
Where do you want to move the video discs to when completed"""),
        ConfigObject("audioripping", "Audio Ripping Location", "string", default="audioripping/",
                     help_text="""
Where do you want to store audio cds while ripping them?"""),
        ConfigObject("audioripped", "Audio Ripped Location", "string", default="audioripped/",
                     help_text="""
Where do you want to move the audio cds to when completed""")
    ]),
    ConfigList("videoripping", "Video Ripping", objects=[
        ConfigObject("enabled", "Enabled", "boolean", default=True, input_type="switch",
                     script=True),
        ConfigObject("torip", "What to Rip", "string_list", default=["movie", "tvshow", "Other"],
                     input_type="checkbox", options=[
                         ConfigOption("movie", "Movie"),
                         ConfigOption("tvshow", "TV Show Episode"),
                         ConfigOption("trailer", "Trailer"),
                         ConfigOption("extra", "Extra"),
                         ConfigOption("other", "Other")
                     ],
                     help_text="What File Types do you want to rip and include"),
    ]),
    ConfigList("audioripping", "Audo CD Ripping", objects=[
        ConfigObject("enabled", "Enabled", "boolean", default=False, input_type="switch",
                     script=True)
    ]),
    ConfigList("converter", "Converter", objects=[
        ConfigObject("enabled", "Enabled", "boolean", default=True, input_type="switch",
                     script=True),
        ConfigObject("ffmpeglocation", "FFmpeg Location", "string", default="ffmpeg",
                     help_text="Where is FFmpeg located?"),
        ConfigObject("ffprobelocation", "FFprobe Location", "string", default="ffprobe",
                     help_text="Where is FFprobe located?"),
        ConfigObject("threadcount", "How Many Instances?", "integer", minimum=1, maximum=5,
                     default=1, help_text="How Many Threads (Max of 5)"),
        ConfigObject("keeporiginalfile", "Keep Original File", "boolean", input_type="checkbox",
                     default=False,
                     help_text="If you want to keep the original file after backup"),
        ConfigObject("defaultlanguage", "Default Language", "option", default="eng",
                     input_type="dropdown", options=Languages().config_option_3t(),
                     help_text="What is your main language?"),
        ConfigObject("videoinserttags", "Insert Tags", "boolean", default=True,
                     input_type="checkbox", help_text="""
Do you want to add in the tags to the Video Files?"""),
        #3D Options Here
        ConfigObject("video3dtype", "3D Type", "option", default='keep',
                     input_type='dropdown',
                     options=[
                         ConfigOption("keep", "Keep Original"),
                         ConfigOption("sbsl", "Side by Side (Left Eye First)"),
                         ConfigOption("sbsr", "Side by Side (Right Eye First)"),
                         ConfigOption("sbs2l", "Half Side by Side (Left Eye First)"),
                         ConfigOption("sbs2r", "Half Side by Side (Right Eye First)"),
                         ConfigOption("abl", "Top Bottom (Left Eye Top)"),
                         ConfigOption("abr", "Top Bottom (Right Eye Top)"),
                         ConfigOption("ab2l", "Half Top Bottom (Left Eye Top)"),
                         ConfigOption("ab2r", "Half Top Bottom (Right Eye Top)"),
                         ConfigOption("al", "Alternating Frames (Left Eye First)"),
                         ConfigOption("ar", "Alternating Frames (Right Eye First)"),
                         ConfigOption("irl", "Interleaved Rows (Left Eye Has Top Row)"),
                         ConfigOption("irr", "Interleaved Rows (Right Eye Has Top Row)"),
                         ConfigOption("arbg", "Anaglyph Red/Blue Grayscale"),
                         ConfigOption("argg", "Anaglyph Red/Green Grayscale"),
                         ConfigOption("arcg", "Anaglyph Red/Cyan Grayscale"),
                         ConfigOption("arch", "Anaglyph Red/Cyan Half Coloured"),
                         ConfigOption("arcc", "Anaglyph Red/Cyan Colour"),
                         ConfigOption("arcd", "Anaglyph Red/Cyan Colour dubois"),
                         ConfigOption("agmg", "Anaglyph Green/Magenta Grayscale"),
                         ConfigOption("agmh", "Anaglyph Green/Magenta Half Coloured"),
                         ConfigOption("agmc", "Anaglyph Green/Magenta Coloured"),
                         ConfigOption("agmd", "Anaglyph Green/Magenta Colour Dubois"),
                         ConfigOption("aybg", "Anaglyph Yellow/Blue Grayscale"),
                         ConfigOption("aybh", "Anaglyph Yellow/Blue Half Coloured"),
                         ConfigOption("aybc", "Anaglyph Yellow/Blue Coloured"),
                         ConfigOption("aybd", "Anaglyph Yellow/Blue Colour Dubois"),
                         ConfigOption("ml", "Mono Output (Left Eye Only)"),
                         ConfigOption("mr", "Mono Output (Right Eye Only)"),
                         ConfigOption("chl", "Checkerboard (Left Eye First)"),
                         ConfigOption("chr", "Checkerboard (Right Eye First)"),
                         ConfigOption("icl", "Interleaved Columns (Left Eye First)"),
                         ConfigOption("icr", "Interleaved Columns (Right Eye First)"),
                         ConfigOption("hdmi", "HDMI Frame Pack")],
                     help_text="what 3D mode do you want to transform 3d Discs into"),
        ConfigObject("videoresolution", "Max Video Resolution", "option", default='keep',
                     input_type='radio',
                     options=[
                         ConfigOption("keep", "Keep Original"),
                         ConfigOption("2160", "4K"),
                         ConfigOption("1080", "1080"),
                         ConfigOption("720", "720"),
                         ConfigOption("sd", "SD")],
                     help_text="What is the maximum resolution you want to keep or downscale to?"),
        ConfigObject("videocodec", "Video Codec", "option", default='keep',
                     input_type='radio',
                     options=[
                         ConfigOption("keep", "Keep Original",
                                      hide=["plugins_ripping_ripper_converter_videopresets",
                                            "plugins_ripping_ripper_converter_x26custom"]),
                         ConfigOption("x264default", "X264 Default",
                                      hide=["plugins_ripping_ripper_converter_videopresets",
                                            "plugins_ripping_ripper_converter_x26custom"]),
                         ConfigOption("x265default", "X265 Default",
                                      hide=["plugins_ripping_ripper_converter_videopresets",
                                            "plugins_ripping_ripper_converter_x26custom"]),
                         ConfigOption("x264custom", "X264 Custom",
                                      show="plugins_ripping_ripper_converter_x26custom",
                                      hide="plugins_ripping_ripper_converter_videopresets"),
                         ConfigOption("x265custom", "X265 Custom",
                                      show="plugins_ripping_ripper_converter_x26custom",
                                      hide="plugins_ripping_ripper_converter_videopresets"),
                         ConfigOption("preset", "Preset (choose from a list)",
                                      show="plugins_ripping_ripper_converter_videopresets",
                                      hide="plugins_ripping_ripper_converter_x26custom")],
                     help_text="What video codec do you wish to convert to?"),
        ConfigList("videopresets", "Video Preset List", objects=[
            ConfigObject("videopreset", "Video Preset", "option",
                         input_type="dropdown", options=video_presets_config_options(),
                         help_text="What preset do you want to use?")],
                   is_section=True, section_link=["plugins", "ripping", "ripper",
                                                  "converter", "videocodec"]),
        ConfigList("x26custom", "x26? Custom Options", objects=[
            ConfigObject("x26crf8bit", "CRF (8 bit)?", "integer", minimum=0, maximum=51,
                         default=23, help_text="""
The range of the CRF (8 bit) scale is 0–51, where 0 is lossless, 23 is the default,and 51 is worst
quality possible. A lower value generally leads to higher quality, and a subjectively sane range is
17–28. Consider 17 or 18 to be visually lossless or nearly so; it should look the same or nearly the
same as the input but it isn't technically lossless. The range is exponential, so increasing the CRF 
value +6 results in roughly half the bitrate / file size, while -6 leads to roughly twice the
bitrate. Choose the highest CRF value that still provides an acceptable quality. If the output looks
good, then try a higher value. If it looks bad, choose a lower value."""),
            ConfigObject("x26crf10bit", "CRF (10 bit)?", "integer", minimum=0, maximum=63,
                         default=23, help_text="""
The range of the CRF (10 bit) scale is 0–63, where 0 is lossless, 23 is the default,and 63 is worst
quality possible."""),
            ConfigObject("x26preset", "Preset", "option", default="medium",
                         input_type="dropdown", options=[ConfigOption("ultrafast", "Ultra Fast"),
                                                         ConfigOption("superfast", "Super Fast"),
                                                         ConfigOption("veryfast", "Very Fast"),
                                                         ConfigOption("faster", "Faster"),
                                                         ConfigOption("fast", "Fast"),
                                                         ConfigOption("medium", "Medium"),
                                                         ConfigOption("slow", "Slow"),
                                                         ConfigOption("slower", "Slower"),
                                                         ConfigOption("veryslow", "Very Slow")],
                         help_text="""
A preset is a collection of options that will provide a certain encoding speed to compression ratio.
A slower preset will provide better compression (compression is quality per filesize).
This means that, for example, if you target a certain file size or constant bit rate,
you will achieve better quality with a slower preset. Similarly, for constant quality encoding,
you will simply save bitrate by choosing a slower preset.
Use the slowest preset that you have patience for."""),
            ConfigObject("x26extra", "Extra commands", "string", default="",
                         help_text="Other commands?")],
                   is_section=True, section_link=["plugins", "ripping", "ripper",
                                                  "converter", "videocodec"]),
        ConfigObject("originalordub", "Original or Dubbed Language", "option", default='all',
                     input_type='radio', options=[ConfigOption("original", "Original"),
                                                  ConfigOption("dub", "Dubbed")],
                     help_text="""
Do you want the default stream to be the Original language or dubbed in your language if available?
"""),
        ConfigObject("audiolanguage", "Audio Languages", "option", default='all',
                     input_type='radio',
                     options=[ConfigOption("all", "All",
                                           hide="plugins_ripping_ripper_converter_audiolanglist"),
                              ConfigOption("original", "Original Language Only",
                                           hide="plugins_ripping_ripper_converter_audiolanglist"),
                              ConfigOption("selectedandoriginal",
                                           "Original Language + Selected Languages",
                                           show="plugins_ripping_ripper_converter_audiolanglist"),
                              ConfigOption("selected", "Selected Languages",
                                           show="plugins_ripping_ripper_converter_audiolanglist")],
                     help_text="What Audio Languages do you want to keep?"),
        ConfigList("audiolanglist", "Audio Language List", objects=[
            ConfigObject("audiolanguages", "Audio Languages", "string_list",
                         input_type="checkbox", options=Languages().config_option_3t())],
                   is_section=True, section_link=["plugins", "ripping", "ripper",
                                                  "converter", "audiolanguage"]),
        ConfigObject("audioformat", "Audio Format", "option", default='all',
                     input_type='radio',
                     options=[
                         ConfigOption("all", "All",
                                      hide="plugins_ripping_ripper_converter_audioformatlist"),
                         ConfigOption("highest", "Highest Quality",
                                      hide="plugins_ripping_ripper_converter_audioformatlist",
                                      disabled=True),
                         ConfigOption("selected", "Selected Formats",
                                      show="plugins_ripping_ripper_converter_audioformatlist")],
                     help_text="What Audio Formats do you want to keep?"),
        ConfigList("audioformatlist", "Audio Format List", objects=[
            ConfigObject("audioformats", "Audio Formats", "string_list",
                         input_type="checkbox", options=audio_format_options)],
                   is_section=True, section_link=["plugins", "ripping", "ripper",
                                                  "converter", "audioformat"]),
        ConfigObject("keepcommentary", "Keep Commentary", "boolean", default=True,
                     input_type="checkbox", help_text="""
Do you want to keep the commentary track(s)?"""),
        #Audio conversion section here (defaulted to off) if user wants to add audio formats
        #   ConfigOption("convert", "Convert to Selected Formats",
        #                show="plugins_ripping_ripper_converter_audioformatlist"),
        ConfigObject("keepchapters", "Keep Chapters", "boolean", default=True,
                     input_type="checkbox", help_text="""
Do you want to keep the chapter points?"""),
        ConfigObject("subtitle", "Subtitles", "option", default='all', input_type='radio',
                     options=[ConfigOption("all", "All",
                                           hide="plugins_ripping_ripper_converter_subtitleslist"),
                              ConfigOption("none", "None",
                                           hide="plugins_ripping_ripper_converter_subtitleslist"),
                              ConfigOption("selected", "Selected Subtitles",
                                           show="plugins_ripping_ripper_converter_subtitleslist")],
                     help_text="What subtitles do you want to keep?"),
        ConfigList("subtitleslist", "Subtitle List", objects=[
            ConfigObject("subtitlelanguages", "Subtitle Languages", "string_list",
                         input_type="checkbox", options=Languages().config_option_3t())],
                   is_section=True, section_link=["plugins", "ripping", "ripper",
                                                  "converter", "subtitle"]),
        ConfigObject("keepclosedcaptions", "Keep Closed Captions", "boolean", default=True,
                     input_type="checkbox", help_text="Do you want to keep the closed captions?"),
    ]),
    ConfigList("drives", "Drives", objects=[
        ConfigObject("enabled", "Enabled", "boolean", default=False, input_type="switch",
                     script=True),
        ConfigObject("name", "Name", "string", default="",
                     help_text="What do you want to call this drive?"),
        ConfigObject("link", "Drive Link", "string", read_only=True, disabled=True,
                     not_in_config=True, value_link=DRIVES,
                     help_text="Adderss of the drive"),
        ConfigObject("model", "Drive Model", "string", read_only=True, disabled=True,
                     not_in_config=True, value_link=DRIVES,
                     help_text="Adderss of the drive")
    ], rules=ConfigRules(for_each=DRIVES))
])

class Plugin(PluginBaseClass):
    '''Main Class to create an instance of the plugin'''

    def __init__(self, plugin_link, name, config, root_config, db, musicbrainz):
        super().__init__(plugin_link, name, config, root_config, db, musicbrainz)
        self._drives = []
        self._video_labeler = VideoLabeler(db, config)
        self._converter = None
        self._renamer = None

        self._db.table_checks("Ripper", db_tables.VIDEO_INFO_DB_INFO)
        self._db.table_checks("Ripper", db_tables.VIDEO_CONVERT_DB_INFO)

        for location in config['locations']:
            folder = config['locations'][location]
            if folder[0] != "/":
                folder = PROGRAMCONFIGLOCATION + config['locations'][location]
            pathlib.Path(folder).mkdir(parents=True, exist_ok=True)

    def startup(self):
        '''Ripper Startup Script'''
        baseurl = self._root_config.get("webui", {}).get("baseurl", "/")
        if platform.system() == 'Linux':
            for drive in DRIVES:
                if drive in self._config['drives']:
                    if self._config['drives'][drive]["enabled"]:
                        self._drives.append(DriveLinux(drive, DRIVES[drive],
                                                       self._config, self._root_config,
                                                       baseurl, self._db))

        #Check if Devices Exist and if not it will stop the plugin from loading
        if not self._drives:
            return False, "No Optical Devices Found or enabled"

        #Start the threads
        for drive in self._drives:
            drive.start_thread()

        if self._config['converter']['enabled']:
            self._converter = Converter(self._config, self._root_config, self._db)
            self._converter.start_thread()

        print("START RENAMER THREAD")
        self._renamer = Renamer(self._config, self._root_config, self._db)
        self._renamer.start_thread()

        self._running = True
        return True, ""

    def shutdown(self):
        '''stop the plugin'''
        for drive in self._drives:
            drive.unlock_tray()
            drive.stop_thread()
        if self._converter is not None:
            RipperEvents().converter.set()
            self._converter.stop_thread()
        if self._renamer is not None:
            RipperEvents().renamer.set()
            self._renamer.stop_thread()
        self._running = False

    def get_drives(self):
        '''gets the drives'''
        return self._drives

    def get_video_labeler(self):
        '''returns the video_labeler system'''
        return self._video_labeler

    def get_converter(self):
        '''returns the converter system'''
        return self._converter
