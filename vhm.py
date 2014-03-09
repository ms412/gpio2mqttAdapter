
import Queue

from config import config
from logAdapter import loghandle
from vdm import vdm


class vhm(object):
    '''
    classdocs
    '''

    def __init__(self,configuration):
        '''
        Constructor
        '''
        self._config = configuration
        self._loghandle = loghandle()
        
        self._threadList = []
        self.threadQueue = Queue.Queue()
        
 #       self._loghandle.info('VHM::init  Version %s , Data %s',__VERSION__,__DATE__)
    #    self._loghandle.info('VHM::init Create Object with configuration %s',configuration)
        
        self.start()
    
    def __del__(self):
        '''
        delets the VHM object
        '''
        self._loghandle.debug('Stop VHM')
        
    def start(self):

        for configurationItem in self._config:
            
  #          device = configurationItem.get('DEVICE')

   #         if 'MCP23017' in device:
            self._loghandle.debug('VHM::Start: Start Device with Configuration: %s', configurationItem)
            threadID = vdm(configurationItem, self.threadQueue)
            threadID.start()
            self._threadList.append(threadID)
  
#            elif 'Simulator' in device:   
#                self._loghandle.debug('VHM::Start: Start Device Simulator with Configuration: %s', configurationItem)           
#                threadID = VirtualDeviceDrvSim(configurationItem, self.threadQueue)
    #            self._loghandle.info('VHM::Start: Start Device Simulator Number of Devices: %s , Objects: %s', len(self._threadList), self._threadList)
#                threadID.start()
#                self._threadList.append(threadID)
 
 #           elif 'Raspberry' in device:
 #               self._loghandle.debug('VHM::Start: Start Device Raspberry with Configuration: %s', configurationItem)
#                threadID = VirtualDeviceDrvRaspberry(configurationItem, self.threadQueue)
    #            self._loghandle.info('VHM::Start: Start Device Raspberry GPIO Number of Devices: %s , Objects: %s', len(self._deviceInstanceList), self._deviceInstanceList)
 #               threadID.start()
 #               self._threadList.append(threadID)
                
  #          else:
   #             self._loghandle.error('VHM::Start: Device not Supported')

        self._loghandle.info('VHM::Start: Number of Threads started: %s',len(self._threadList))
        
    def Write(self, channel, port, value):
        """
        Write to port
        Channel = MqttChannel
        port = name of port
        value = value to be written to port
        """
        result = False

        result,threadID = self.GetThreadID(channel)
        
        if result == True:
            self._loghandle.info('VHM::Write Device Found: %s', channel)
    #        print "Write to Device", channel
            threadID.Write(port,value)
        else:
            self._loghandle.error('VHM::Write Device %s not Found', channel)
            result = False
        
        return result
        
    def Read(self, channel, port):
        result,threadID = self.GetThreadID(channel)
        
        if result == True:
            self._loghandle.debug('VHM::Read Device Found: %s', channel) 
            result, value = threadID.Read(port)
            if result == True:
                self._loghandle.debug('VHM::Read Channel: %s, Port: %s, Status: %s', channel, port, value)
            else:
                self._loghandle.error('VHM::Read Port not Found')
                result = False
        else:
            self._loghandle.error('VHM::Write Device %s not Found', channel)
            result = False
            
        return(result,value)      

    def Update(self):
        resultList = []
        
      #  self._loghandle.debug('VHM::Update size of Queue %s', self.threadQueue.qsize())
        while self.threadQueue.qsize():
            data = self.threadQueue.get()
            for item in data:
                self._loghandle.debug('VHM::Update Queue output %s', item)
            
                resultList.append(item)
    
       # self._loghandle.debug('VHM::Update Data Object %s', resultList)
        return resultList
        

    def GetThreadID(self, channel):
        """
        Seach all instances for Channel Name
        """  
        
        result = False
        ret_threadID = None

        for threadID in self._threadList:
            print "Search thread Search: ", channel," thread name", threadID.GetChannelName()
            if channel in threadID.GetChannelName():
                ret_threadID = threadID
                result = True
                print "Thread FOUND"
                break
                
        return (result,ret_threadID)  
    
    def ThreadMonitor(self):
        
        result = False
        
        for threadID in self._threadList:
            if threadID.isAlive() == True:
                result = True
            else:
                result = False
                self._loghandle.critical('VHM::ThreadMonitor: One Thread crashed ThreadID: %s',threadID)
                break
        
        return result
    
    def RequestSync(self):
        
        for threadID in self._threadList:
            threadID.RequestSync()
