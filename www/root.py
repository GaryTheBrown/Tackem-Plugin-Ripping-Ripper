'''Root pages'''
import cherrypy
from libs.html_template import HTMLTEMPLATE
from . import html_parts

class Root(HTMLTEMPLATE):
    '''ROOT OF PLUGINS WEBUI HERE'''
    @cherrypy.expose
    def index(self):
        '''index of plugin'''
        self._tackem_system.get_auth().check_auth()
        baseurl = self._tackem_system.get_baseurl()
        root_html = html_parts.get_page("root/index")
        drives_html = html_parts.drives(self._tackem_system.system().get_drives(),
                                        self._tackem_system.config()['drives'], True)
        root_html = root_html.replace("%%DRIVES%%", drives_html)
        thread_name = "WWW" + cherrypy.request.remote.ip
        labeler_data = self._tackem_system.system().get_video_labeler().get_data(thread_name)
        #TODO FOR AUDIO LABELER
        root_html = root_html.replace("%%AUDIOLABELERS%%", "")
        root_html = root_html.replace("%%VIDEOLABELERS%%",
                                      html_parts.video_labeler_items(labeler_data, baseurl, True))
        #TODO FOR AUDIO LABELER
        audio_count = 0
        video_count = self._tackem_system.system().get_video_labeler().get_count(thread_name)
        if audio_count > 0:
            root_html = root_html.replace("%%AUDIOLABLERCOUNT%%", str(audio_count))
        else:
            root_html = root_html.replace(" (%%AUDIOLABLERCOUNT%%)", "")
        if video_count > 0:
            root_html = root_html.replace("%%VIDEOLABLERCOUNT%%", str(video_count))
        else:
            root_html = root_html.replace(" (%%VIDEOLABLERCOUNT%%)", "")
        #need to add the audio convertor data here as well
        converter_data = self._tackem_system.system().get_converter().get_data()
        root_html = root_html.replace("%%CONVERTERS%%", html_parts.converter_items(converter_data))
        return self._template(root_html)
