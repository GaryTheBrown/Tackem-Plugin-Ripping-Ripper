'''WEBUI FOR PLUGIN'''
import os
import cherrypy
from libs.startup_arguments import PROGRAMCONFIGLOCATION
from .root import Root
from .drives import Drives
from .video_labeler import VideoLabeler
from .converter import Converter

LAYOUT = {}
def mounts(key, systems, plugins, config, auth):
    '''where the system creates the cherrypy mounts'''
    stylesheet = key.replace(" ", "/") + "/static/style.css"
    root = Root("Ripper", key, systems, plugins, config, auth, base_stylesheet=stylesheet)
    root.drives = Drives("Ripper Drives", key, systems, plugins, config, auth,
                         base_stylesheet=stylesheet)
    root.videolabeler = VideoLabeler("Ripper Video Labeler", key, systems, plugins, config, auth,
                                     base_stylesheet=stylesheet)
    root.converter = Converter("Ripper Video Converter", key, systems, plugins, config,
                               auth, base_stylesheet=stylesheet)
    cherrypy.tree.mount(root,
                        config.get("webui", {}).get("baseurl", "/") + key.replace(" ", "/") + "/",
                        cfg(config))

def cfg(config):
    '''generate the cherrypy conf'''
    temp_config = config['plugins']['ripping']['ripper']['locations']
    temp_video_location = temp_config['videoripping']
    if temp_config['videoripping'][0] != "/":
        temp_video_location = PROGRAMCONFIGLOCATION + temp_config['videoripping']
    temp_audio_location = temp_config['audioripping']
    if temp_config['audioripping'][0] != "/":
        temp_audio_location = PROGRAMCONFIGLOCATION + temp_config['audioripping']

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
