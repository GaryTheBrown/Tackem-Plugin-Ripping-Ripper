'''Get Movie API'''
import cherrypy
from api.base import APIBase
from config_data import CONFIG

@cherrypy.expose
class APIScraperGetMovie(APIBase):
    '''Get Movie API'''

    def POST(self, **kwargs) -> str:
        '''POST Function'''
        user = kwargs.get("user", self.GUEST)
        required = []
        if (plugin_type:= kwargs.get("plugin_type", "")) == "":
            required.append("plugin_type")
        if (plugin_name:= kwargs.get("plugin_name", "")) == "":
            required.append("plugin_name")
        if (instance:= kwargs.get("instance", "")) == "":
            required.append("instance")
        if required:
            return self._return_data(
                user,
                "addMulti",
                "Adding Instance of {} - {}".format(plugin_type, plugin_name),
                False,
                instance=instance,
                error="Missing Data Passed. Requires {}".format(
                    ", ".join(required)),
                errorNumber=0
            )

        var = instance.lower().replace(" ", "")
        if var in CONFIG["plugins"][plugin_type][plugin_name].keys():
            return self._return_data(
                user,
                "addMulti",
                "Adding Instance of {} - {}".format(plugin_type, plugin_name),
                False,
                instance=instance,
                error="Instance already exists",
                errorNumber=1
            )

        if not CONFIG["plugins"][plugin_type][plugin_name].clone_many_section(instance):
            return self._return_data(
                user,
                "addMulti",
                "Adding Instance of {} - {}".format(plugin_type, plugin_name),
                False,
                instance=instance,
                error="Cloning Data Failed",
                errorNumber=2
            )

        variable_name = "plugins_{}_{}".format(
            plugin_type, plugin_name)
        return self._return_data(
            user,
            "config",
            "Adding Instance of {} - {}".format(plugin_type, plugin_name),
            True,
            instance=instance,
            html=CONFIG["plugins"][plugin_type][plugin_name][instance].panel(
                variable_name,
                instance.title()
            )
        )

    # def getmovie(self, movie_id) -> str:
    #     '''get movie by TMDB id'''
    #     return self._get_movie_details(movie_id)
