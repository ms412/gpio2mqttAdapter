

import logging

# Singleton/SingletonDecorator.py
class SingletonDecorator:
    def __init__(self,klass):
        self.klass = klass
        self.instance = None
    def __call__(self,*args,**kwds):
        if self.instance == None:
            self.instance = self.klass(*args,**kwds)
        return self.instance

class loggingwrapper:
    '''
    classdocs
    '''


    def open(self, LOGFILE,LOGMODE):
        '''
        Constructor
        '''
 #       logging.__init__(self)
        LOGFORMAT = '%(asctime)-15s - %(levelname)s - %(message)s'
        LOGFORMAT_DEBUG = '%(asctime)-15s - %(message)s'


        if 'INFO' in LOGMODE:
            logging.basicConfig(filename=LOGFILE, level=logging.INFO, format=LOGFORMAT)
        elif 'WARNING' in LOGMODE:
            logging.basicConfig(filename=LOGFILE, level=logging.WARNING, format=LOGFORMAT)
        elif 'ERROR' in LOGMODE:
            logging.basicConfig(filename=LOGFILE, level=logging.ERROR, format=LOGFORMAT)
        elif 'CRITICAL' in LOGMODE:
            logging.basicConfig(filename=LOGFILE, level=logging.CRITICAL, format=LOGFORMAT)  
        else:
            logging.basicConfig(filename=LOGFILE, level=logging.DEBUG, format=LOGFORMAT_DEBUG)        
            
    def info(self,msg, *args, **kwargs):
        logging.info(msg, *args, **kwargs)
        
    def warning(self,msg, *args, **kwargs):
        logging.warning(msg, *args, **kwargs)

    def error(self,msg, *args, **kwargs):
        logging.error(msg,*args, **kwargs)
        
    def critical(self,msg, *args, **kwargs):
        logging.critical(msg, *args, **kwargs)
        
    def debug(self, msg, *args, **kwargs):
        logging.debug(msg, *args, **kwargs)
        
        
loghandle = SingletonDecorator(loggingwrapper)
