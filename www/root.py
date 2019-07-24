'''Root pages'''
import cherrypy
from libs.html_template import HTMLTEMPLATE
from . import html_parts

class Root(HTMLTEMPLATE):
    '''ROOT OF PLUGINS WEBUI HERE'''
    @cherrypy.expose
    def index(self):
        '''index of plugin'''
        self._auth.check_auth()
        baseurl = self._global_config.get("webui", {}).get("baseurl", "/")
        root_html = html_parts.get_page("root/index")
        root_html = root_html.replace("%%DRIVES%%", html_parts.drives(self._system.get_drives(),
                                                                      self._config['drives'], True))
        labeler_data = self._system.get_video_labeler().get_data("WWW" + cherrypy.request.remote.ip)
        #TODO FOR AUDIO LABELER
        root_html = root_html.replace("%%AUDIOLABELERS%%", "")
        root_html = root_html.replace("%%VIDEOLABELERS%%",
                                      html_parts.video_labeler_items(labeler_data, baseurl, True))
        #TODO FOR AUDIO LABELER
        audio_labeler_count = 0
        thread_name = "WWW" + cherrypy.request.remote.ip
        video_labeler_count = self._system.get_video_labeler().get_count(thread_name)
        if audio_labeler_count > 0:
            root_html = root_html.replace("%%AUDIOLABLERCOUNT%%", str(audio_labeler_count))
        else:
            root_html = root_html.replace(" (%%AUDIOLABLERCOUNT%%)", "")
        if video_labeler_count > 0:
            root_html = root_html.replace("%%VIDEOLABLERCOUNT%%", str(video_labeler_count))
        else:
            root_html = root_html.replace(" (%%VIDEOLABLERCOUNT%%)", "")
        #need to add the audio convertor data here as well
        converter_data = self._system.get_converter().get_data()
        root_html = root_html.replace("%%CONVERTERS%%", html_parts.converter_items(converter_data))
        return self._template(root_html)
