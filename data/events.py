'''Ripper Global Events'''
import threading

class RipperEvents:
    '''Ripper Global Events'''
    converter = threading.Event()
    renamer = threading.Event()
