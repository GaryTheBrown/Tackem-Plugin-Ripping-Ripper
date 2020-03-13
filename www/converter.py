'''Converter pages'''
import json
import cherrypy
from libs.authenticator import AUTHENTICATION
from libs.html_template import HTMLTEMPLATE
from libs import html_parts as ghtml_parts
from . import html_parts


class Converter(HTMLTEMPLATE):
    '''CONVERTER WEBUI'''

    def _return(self):
        '''return on fail'''
        raise cherrypy.HTTPRedirect(self._baseurl + "ripping/ripper/")

    @cherrypy.expose
    def index(self):
        '''index page return to ripper main page'''
        self._return()

    @cherrypy.expose
    def single(self, index=None):
        '''get single converter item'''
        AUTHENTICATION.check_auth()
        if index is None:
            self._return()
        try:
            index_int = int(index)
        except ValueError:
            self._return()
        data = self._tackem_system.system().get_converter().get_data_by_id(index_int)
        if data is False:
            self._return()
        return html_parts.converter_item(data)

    @cherrypy.expose
    def getids(self):
        '''index of Drives'''
        AUTHENTICATION.check_auth()
        return json.dumps(self._tackem_system.system().get_converter().get_data_ids())

    @cherrypy.expose
    def getconverting(self, index=None):
        '''get single converter item'''
        AUTHENTICATION.check_auth()
        if index is None:
            self._return()
        try:
            index_int = int(index)
        except ValueError:
            self._return()
        return str(self._tackem_system.system().get_converter().get_converting_by_id(index_int))

    @cherrypy.expose
    def progress(self, index=None):
        '''get progress bar item'''
        AUTHENTICATION.check_auth()
        if index is None:
            self._return()
        try:
            index_int = int(index)
        except ValueError:
            self._return()
        data = self._tackem_system.system().get_converter().get_data_by_id(index_int)
        if data is False:
            self._return()
        if data['converting']:
            label = str(data['process']) + "/" + str(data['count'])
            label += "(" + str(data['percent']) + "%)"
            return ghtml_parts.progress_bar(label, str(data['process']), str(data['count']),
                                            data['percent'])
        return ""
