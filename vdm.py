
import threading
import Queue
import time


from vpm import BinaryOut
from vpm import BinaryIn
from vpm import TimerOut
from vpm import TimerIn
from vpm import S0
from hwIF_23017 import hwIF_23017
from hwIF_raspberry import hwIF_raspberry

from config import config
from logAdapter import loghandle



class vdm(threading.Thread):
    '''irtualDeviceDrv23017
    classdocs
    '''

    def __init__(self, configuration, fromPortQueue):
        '''
        Constructor
        '''
        threading.Thread.__init__(self)
        
        self._loghandle = loghandle()

        self._config = config(configuration)
        
        self._help = configuration
        
        self._DEVICE_TYPE = configuration.get('TYPE')
        self._DEVICE_NAME = configuration.get('NAME')
        self._MQTT_CHANNEL = configuration.get('MQTT_CHANNEL')
        self._THREAD_UPDATE = float(configuration.get('UPDATE',0.1))
        
        self._fromPortQueue = fromPortQueue
        
        self._portInstanceList = []
        
        self._requestSync = False
#        self._loghandle.info('VirtualDeviceDrv23017::init  Version %s , Date %s',__VERSION__,__DATE__)
        self._loghandle.info('VDM::init Create Object Device %s Mqtt %s',self._DEVICE_TYPE, self._DEVICE_NAME)
        self._loghandle.debug('VDM::init Create Object with configuration %s',configuration)
        
    def __del__(self):
        '''
        delets the mqtt wrapper object
        '''
        self._loghandle.debug('VDM::del Delete Object')
        
    def run(self):
        self._loghandle.info('VDM::run Startup Thread')
        
        self.Setup()
   #     self.SetupPort()
        
        #read the port status of all boards 
       # data = self.Read()
      #  self._fromPortQueue.put(data)
        data = self.Get('ALL')
        
        print data
        rc = 0
        while rc == 0:
            
            data = self.Get('UPDATE')
            
         #   print "UPDATE:",len(data),data
            self._fromPortQueue.put(data)
            
  #          print "Simulator Loop"
            '''Read Updaet from GPIO Ports'''
        #    data = self.Update()
         #   self._fromPortQueue.put(data)
            
            if self._requestSync == True:
                data = self.Get('ALL')
                self._fromPortQueue.put(data)
                self._requestSync = False
                self._loghandle.info('Sync all ports %s',data)
            ''' make update from Flash Ports'''
   #         self.UpdateFlash()
   #         self.UpdatePushButton()
    #        data = self.UpdateDebounce()
     #       self._threadQueue.put(data)
    #        time.sleep(3)
     #       data = self.Get('ALL')
      #      print "ALL:",len(data), data
            time.sleep(self._THREAD_UPDATE)
            
        #    while self._toPortQu.qsize:
                
                 #   def SetupPort(self):

  #      for configItem in self._config.getSectionByRegex('Port[0-9]'): 
   #         self._loghandle.debug('VirtualDeviceDrv23017::SetupPort Port %s', configItem) 
   #         self._portInstanceList.append(virtualPort(self._hwDevice, configItem))e():
            #    print self._setQueue.qsize()
           #     print self._setQueue.get()
            #    time.sleep(1)

        self._loghandle.critical('VDM::run Thread Crashed')
        return rc
        
    def Setup(self):
        if 'MCP23017' in self._DEVICE_TYPE:
            self._RASPBERRY_REV = int(self._help.get('RASPBERRY_REV'))
            self._I2C_ADDRESS = int(self._help.get('I2C_ADDRESS'),16)
            self._loghandle.info('Start MCP23017 Hardware Interface with i2c address: %s',self._I2C_ADDRESS)
            self._hwHandle = hwIF_23017(self._RASPBERRY_REV,self._I2C_ADDRESS)
           
            for configItem in self._config.getSectionByRegex('Port[0-9]'): 
                self._loghandle.debug('VirtualPortManager:Setup Port Number %s for Device %s with Configuration',len(self._portInstanceList), self._DEVICE_TYPE, configItem) 
                if 'BINARY-OUT' in configItem.get('MODE'):
                    self._portInstanceList.append(BinaryOut(self._hwHandle, self._DEVICE_TYPE, configItem))
                elif 'BINARY-IN' in configItem.get('MODE'):
                    self._portInstanceList.append(BinaryIn(self._hwHandle, self._DEVICE_TYPE, configItem))
                elif 'TIMER-OUT' in configItem.get('MODE'):
                    self._portInstanceList.append(TimerOut(self._hwHandle, self._DEVICE_TYPE, configItem))
                elif 'TIMER-IN' in configItem.get('MODE'):
                    self._portInstanceList.append(TimerIn(self._hwHandle, self._DEVICE_TYPE, configItem))
                elif 'S0' in configItem.get('MODE'):
                    self._portInstanceList.append(S0(self._hwHandle, self._DEVICE_TYPE, configItem))
                else:
                    self._loghandle.critical('VirtualPortManager:Setup Port Number %s for Device %s Mode %s not supported',configItem.get('NAME'), self._DEVICE_TYPE, configItem.get('MODE')) 
                
        elif 'RASPBERRY' in self._DEVICE_TYPE:
            self._loghandle.info('Start Raspberry GPIO interface')
            self._hwHandle = hwIF_raspberry()
            
            for configItem in self._config.getSectionByRegex('Port[0-9]'): 
                self._loghandle.debug('VirtualPortManager:Setup Port Number %s for Device    OFF_VALUE: OFF %s with Configuration',len(self._portInstanceList), self._DEVICE_TYPE, configItem) 
                self._portInstanceList.append(S0(self._hwHandle, self._DEVICE_TYPE, configItem))
                
        else:
            self._loghandle.crittical('VDM::Setup: Device not Supported')
            
        
        return True
                       
    def Write(self, portName, value):  
     
        resultDict = self.GetPortInstance(portName)             
        result = resultDict.get('Result')
        instance = resultDict.get('Instance')
        
        if result == True:
            
            if 'OUT' in instance.GetDirection(): 
                self._loghandle.debug('VDM::Write Port %s found in Portlist', portName)
                instance.Set(value)
                
            else:
                self._loghandle.debug('VDM::Write Port %s is not OUTPUT Port', portName)
                result = False
        else:
            self._loghandle.error('VDM::Write Port %s NOT found in Portlist', portName)
            result = False

        return result
    
    def Read(self, name = None):
        
        resultList =[]
        
        if name != None:
            resultDict = self.GetPortInstance(portName)             
            result = resultDict.get('Result')
            instance = resultDict.get('Instance')
            if result == True:
                value = instance.Get()
                resultList.append(self.EnrichResult(value, instance))
                
        else:
            for instance in self._portInstanceList:
                if 'TIMER-OUT' in instance.GetMode():
                    break
                    
                else:
                    value = instance.Get()
                    resultList.append(self.EnrichResult(value, instance))
                
    #    print 'GET',resultList
        return resultList
    
    def Get(self, mode = None):
        
        resultList = []
        
        for instance in self._portInstanceList:     
            if 'BINARY-IN' in instance.GetMode():
                if instance.Update() == True or 'ALL' in mode:
        #        if instance.Update() == True:
             #       print instance.Update()
                    resultList.append(self.Get_Port(instance))
            elif 'BINARY-OUT' in instance.GetMode():
                if'ALL' in mode:
                    resultList.append(self.Get_Port(instance))
            elif 'TIMER-OUT'in instance.GetMode():
               # print "Timer Out", instance.Update()
                if instance.Update() == True or 'ALL' in mode:
              #      print "TIMER-OUT"
                    resultList.append(self.Get_Port(instance))
            elif 'TIMER-IN' in instance.GetMode():
                if instance.Update() == True or 'ALL' in mode:
                #    print "TIMER-IN"
                    resultList.append(self.Get_Port(instance))
            elif 'S0' in instance.GetMode():
                if instance.Update() == True or 'ALL' in mode:
                #    print "TIMER-IN"
                    resultList.append(self.Get_Port(instance))
            else:
                print 'unknown'
                
 #       print "Length",len(resultList),"Content",resultList
    
        return resultList
    
    def Get_Port(self, instance):
        
        resultDict ={}

        portDict = instance.Get()
        
 #       print "Debug",portDict
            
        if portDict.get('STATE') == True:
            resultDict.update({'DEVICE_NAME':self._DEVICE_NAME})
            resultDict.update({'PORT_NAME':portDict.get('NAME')})
            resultDict.update({'PORT_VALUE':portDict.get('VALUE')})
        else:
            self._loghandle.debug('VDM::GetBinaryIn data invalid Return State: %s', portDict.get('STATE')) 
 #       print "Result Dict:",resultDict
        return resultDict
    
    def Get_BinaryOut(self, instance):
        
        resultDict ={}
        
        portDict = instance.Get()

        if portDict.get('STATE') == True:
            resultDict.update({'DEVICE_NAME':self._DEVICE_NAME})
            resultDict.update({'PORT_NAME':portDict.get('NAME')})
            resultDict.update({'PORT_VALUE':portDict.get('VALUE')})
        else:
            self._loghandle.debug('VDM::GetBinaryOut data invalid Return State: %s', portDict.get('STATE')) 

        return resultDict
    
    def Get_TimerOut(self,instance):
        
        resultDict ={}
        
        portDict = instance.Get()

        if portDict.get('STATE') == True:
            resultDict.update({'DEVICE_NAME':self._DEVICE_NAME})
            resultDict.update({'PORT_NAME':portDict.get('NAME')})
            resultDict.update({'PORT_VALUE':portDict.get('VALUE')})
        else:
            self._loghandle.debug('VDM::GetTimerOut data invalid Return State: %s', portDict.get('STATE')) 

        return resultDict
    
    def Get_TimerIn(self,instance):
        
        resultDict ={}
        
        portDict = instance.Get()

        if portDict.get('STATE') == True:
            resultDict.update({'DEVICE_NAME':self._DEVICE_NAME})
            resultDict.update({'PORT_NAME':portDict.get('NAME')})
            resultDict.update({'PORT_VALUE':portDict.get('DELTA_T1')})
            resultDict.update({'DELTA_T1':portDict.get('DELTA_T1')})
        else:
            self._loghandle.debug('VDM::GetTimerIn; data invalid Return State: %s', portDict.get('STATE')) 

        return resultDict            

    def UpdateOld(self, mode = 'UPDATE'):
        
        resultList =[]
        
        for instance in self._portInstanceList:
            if 'BINARY-IN' in instance.GetMode():
#            if 'IN' in instance.GetDirection():
                value = instance.Update()
                if value.get('Update') == True:
                    resultList.append(self.EnrichResult(value.get('State'), instance))
                    
            elif 'TIMER-OUT' in instance.GetMode():
                instance.Update()
                
            elif 'TIMER-IN' in instance.GetMode():
                value = instance.Update()
                if value.get('Update') == True:
                    resultList.append(self.EnrichResult(value.get('State'), instance))
     #   print 'UPDATE',resultList    
        return resultList
    

            
        
    def EnrichResult(self, value, instance):
        
        resultDict = {}
        
        resultDict.update({'DEVICE_NAME':self._DEVICE_NAME})
        resultDict.update({'PORT_NAME':instance.GetName()})
        resultDict.update({'PORT_STATE':value})
        
        return resultDict
    
    def RequestSync(self):
        self._requestSync = True
        
    def UpdateGPIO(self, mode):
        resultList = []
        
        for portInstance in self._portInstanceList:
            if 'UPDATE' in mode:
                if 'IN' in portInstance.GetDirection():
                    resultDict = portInstance.UpdateGPIO()
                    if resultDict.get('Update') == True:   
                        resultDict.update({'DeviceChannel':self._MQTT_CHANNEL})
                        resultDict.update({'PortName':portInstance.GetName()})
                        resultDict.update({'PortState':resultDict.get('State',None)})
                        resultList.append(resultDict)
                        
            elif 'ALL' in mode:

                resultDic = portInstance.Get()
            
                resultDic.update({'DeviceChannel':self._MQTT_CHANNEL})
                resultDic.update({'PortName':portInstance.GetName()})
                resultDic.update({'PortState':resultDic.get('State',None)})

                resultList.append(resultDic)
            
            else:
                self._loghandle.error('VirtualDeviceDrv23017::Update unknown Mode: %s', mode)  
                
        if len(resultList) > 1:
            self._loghandle.info('VirtualDeviceDrv23017::Update Result List %s', resultList)  
            
        return resultList
    
    def UpdateFlash(self):
        
        for portInstance in self._portInstanceList:
            if 'FLASH' in portInstance.GetMode():
                portInstance.UpdateFlash()   
                
    def UpdatePushButton(self):
        
        for portInstance in self._portInstanceList:
            if 'PUSH_BUTTON' in portInstance.GetMode():
                portInstance.UpdatePushButton()   
                
    def UpdateDebounce(self):    
        resultList = [] 
        
        for portInstance in self._portInstanceList:
            if 'DEBOUNCE' in portInstance.GetMode():
                resultDict = portInstance.UpdateDebounce()
                if resultDict.get('Update') == True: 
                    resultDict.update({'DeviceChannel':self._MQTT_CHANNEL})
                    resultDict.update({'PortName':portInstance.GetName()})
                    resultDict.update({'PortState':resultDict.get('State',None)})
                    
                    resultList.append(resultDict)
                    
        if len(resultList) > 1:
            self._loghandle.info('VirtualDeviceDrv23017::UpdateDebounce Result List %s', resultList)
  
        return resultList
 #       return resultList
          
     
    def GetPortInstance(self, portName):    

        result = False
        portInstance = None
        
        portName = portName.strip()
        
        for instance in self._portInstanceList:
  #          print "Search instance Search: ", portName," instance name", instance.GetName()
            if portName == instance.GetName():
    #            self._loghandle.info('DRIVER_Simulator::TEst Portname %s, GetName() %2', portName, instance.GetName())
                portInstance = instance
                result = True
   #             print "Port FOUND"
                break
                
        self._loghandle.debug('VirtualDeviceDrv23017::GetPortInstance Result: %s Port Instance %s', result, portInstance)       
      #  return (result, portInstance)    
        return {'Result':result,'Instance':portInstance}

    
    def GetChannelName(self):
        return self._DEVICE_NAME
        

    
             