'''shared infor between video ripper and audio cd ripper'''

class RipperSubSystem():
    '''Subsystem controller'''
    def __init__(self, device, config, db, thread_name, set_drive_status, thread_run):
        self._device = device
        self._config = config
        self._db = db
        self._thread_name = thread_name
        self._thread_run = thread_run
        self._set_drive_status = set_drive_status

        self._ripping_track = None
        self._ripping_file = 0
        self._ripping_total = 0
        self._ripping_max = 0
        self._ripping_file_p = 0.0
        self._ripping_total_p = 0.0

###########
##GETTERS##
###########
    def get_ripping_data(self):
        '''returns the data as dict for html'''
        return_dict = {
            'track':self._ripping_track,
            'file':self._ripping_file,
            'total':self._ripping_total,
            'max':self._ripping_max,
            'file_percent':self._ripping_file_p,
            'total_percent':self._ripping_total_p
        }
        return return_dict
