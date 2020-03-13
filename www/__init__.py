'''WEBUI FOR PLUGIN'''
import os
import cherrypy
from libs.startup_arguments import PROGRAMCONFIGLOCATION
from system.plugin import TackemSystemPlugin
from config_data import CONFIG
from .root import Root
from .drives import Drives
from .video_labeler import VideoLabeler
from .converter import Converter

LAYOUT = {}


def mounts(key, instance_name=None):  # take tackem_system off the line and generate it inside pass
    # it through to the html template that should take it as as argument so some windows have full
    # others have limited access to system data
    '''where the system creates the cherrypy mounts'''
    tackem_system = TackemSystemPlugin("ripping", "ripper", instance_name)
    stylesheet = key.replace(" ", "/") + "/static/style.css"
    root = Root("Ripper", key, tackem_system, base_stylesheet=stylesheet)
    root.drives = Drives("Ripper Drives", key,
                         tackem_system, base_stylesheet=stylesheet)
    root.videolabeler = VideoLabeler("Ripper Video Labeler", key, tackem_system,
                                     base_stylesheet=stylesheet)
    root.converter = Converter("Ripper Video Converter", key, tackem_system,
                               base_stylesheet=stylesheet)
    cherrypy.tree.mount(
        root,
        CONFIG['webui']['baseurl'].value + key.replace(" ", "/") + "/",
        cherrypy_cfg()
    )


def cherrypy_cfg():
    '''generate the cherrypy conf'''
    config = CONFIG['plugins']['ripping']['ripper']
    temp_video_location = config['locations']['videoripping'].value
    if config['locations']['videoripping'].value[0] != "/":
        temp_video_location = PROGRAMCONFIGLOCATION
        temp_video_location += config['locations']['videoripping'].value
    temp_audio_location = config['locations']['audioripping'].value
    if config['locations']['audioripping'].value[0] != "/":
        temp_audio_location = PROGRAMCONFIGLOCATION
        temp_audio_location += config['locations']['audioripping'].value

    conf_root = {
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.dirname(__file__) + '/static/'
        },
        '/tempvideo': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': temp_video_location
        },
        '/tempaudio': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': temp_audio_location
        }
    }

    return conf_root
