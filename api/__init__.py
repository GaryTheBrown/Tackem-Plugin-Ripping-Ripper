'''PLUGIN API ROOT'''
import cherrypy
from api.system_base import APISystemBase


@cherrypy.expose
class API(APISystemBase):
    '''PLUGIN API ROOT'''

    def _cp_dispatch(self, vpath):
        '''cp dispatcher overwrite'''
        # action = vpath.pop(0)

        return self
