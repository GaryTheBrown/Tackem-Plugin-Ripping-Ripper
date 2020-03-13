'''drives pages'''
import cherrypy
from libs.authenticator import AUTHENTICATION
from libs.html_template import HTMLTEMPLATE


class Drives(HTMLTEMPLATE):
    '''DRIVES WEBUI'''

    def _return(self):
        '''return on fail'''
        raise cherrypy.HTTPRedirect(self._baseurl + "ripping/ripper/")

    @cherrypy.expose
    def index(self):
        '''index page return to ripper main page'''
        self._return()

    @cherrypy.expose
    def single(self, index=None):
        '''get single Drive'''
        AUTHENTICATION.check_auth()
        if index is None:
            self._return()
        try:
            index_int = int(index)
        except ValueError:
            self._return()
        drives = self._tackem_system.system().get_drives()
        if index_int > len(drives):
            self._return()
        drive = self._tackem_system.system().get_drives()[index_int]
        return drive.html_data()
