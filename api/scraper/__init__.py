'''SCRAPER ROOT API'''
import cherrypy
from api.base import APIBase
from .find_movie import APIScraperFindMovie
from .find_tvshow import APIScraperFindTvshow
from .get_movie import APIScraperGetMovie
from .get_tvshow import APIScraperGetTvshow
from .search_movie import APIScraperSearchMovie
from .search_tvshow import APIScraperSearchTvshow

@cherrypy.expose
class APIAdmin(APIBase):
    '''ROOT API'''

    def _cp_dispatch(self, vpath):
        '''cp dispatcher overwrite'''
        if len(vpath) == 0:
            return self

        section = vpath.pop(0)

        if section == "findmovie":
            return APIScraperFindMovie()
        if section == "findtvshow":
            return APIScraperFindTvshow()
        if section == "getmovie":
            return APIScraperGetMovie()
        if section == "gettvshow":
            return APIScraperGetTvshow()
        if section == "searchmovie":
            return APIScraperSearchMovie()
        if section == "searchtvshow":
            return APIScraperSearchTvshow()
        return self
