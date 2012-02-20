'''
Created on Feb 19, 2012

@author: alex
'''

class XBMCVideoPluginHandler(object):
    '''This is a base class for a handler.  Subclass this and define
    a run method.'''
    def __init__(self, argv0, argv1, app, argsdict):
        self.argv0 = argv0
        self.argv1 = int(argv1)
        self.args = argsdict
        self.app = app

    def run(self):
        raise NotImplementedError