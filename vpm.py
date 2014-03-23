
import time
import json

from logAdapter import loghandle

class BinaryOut(object):
    '''
    classdocs
    '''
    def __init__(self, hwHandle, hwDevice, configuration):
        '''
        Constructor
        '''    

        self._hwHandle = hwHandle
        self._hwDevice = hwDevice
        self._config = configuration
        self._loghandle = loghandle()
        
        self.Setup()
        
    def Setup(self):
        
   #     self._SavePinState = ''
        
 
        if any(temp in self._hwDevice for temp in ['MCP23017','RASPBERRY']):
            ''' 
            Mandatory configuration Items
            '''
            try:
                self._NAME = self._config.get('NAME')
                self._HWID = int(self._config.get('HWID'))
                self._MODE = self._config.get('MODE')

            except:
                self._loghandle.critical('VPM::Init Mandatory Parameter missing for Port %s',self._NAME)
                
            ''' 
            optional configuration Items
            '''
            self._DIRECTION = self._config.get('DIRECTION','OUT')
            self._OFF_VALUE = self._config.get('OFF_VALUE','OFF')
            self._ON_VALUE = self._config.get('ON_VALUE','ON')
            self._INITIAL = self._config.get('INITIAL',None)
            
            '''
            Define class variables
            '''
            self._SavePinState = ''
            
            '''
            configure port as Output
            '''
            self._hwHandle.ConfigIO(self._HWID,0)
            
            ''' 
            set initial configuration
            '''
            if self._INITIAL != None:
                self.Set(self._INITIAL)
            
                
            self._loghandle.info('VPM::Init Configure Port %s HardwareID %s in Mode %s',self._NAME,self._HWID,self._MODE)

        else:
            self._loghandle.crittical('VDM::Setup: Device not Supported')
            
        return True
            
    def Set(self,value):
        ''' 
        Port set port polarity; value as defined in ON_VALUE or OFF_VALUE
        '''
        if self._ON_VALUE in value:
            self._hwHandle.WritePin(self._HWID, 1)
            self._SavePinState  = 1
            self._loghandle.info('BinaryOut::Set %s port %s set to %s',self._NAME,self._HWID, value)  
                     
        elif self._OFF_VALUE in value:
            self._hwHandle.WritePin(self._HWID, 0) 
            self._SavePinState  = 0
            self._loghandle.info('BinaryOut::Set %s port %s set to %s',self._NAME,self._HWID, value) 
             
        else:
            self._loghandle.error('BinaryOut::Set %s port %s command NOT %s found',self._NAME,self._HWID, value)  
    
        return True
 
            
    def Get(self):
        '''
        Returns current state of port in Dictionary
        VALUE: as defined in ON/OFF_VALUE
        STATE: True/False whether VALUE true or false
        '''
        value = ''
        name = self._NAME
        state = False
        
        if self._hwHandle.ReadPin(self._HWID) == 0:
            self._SavePinState  = 0
            value = self._OFF_VALUE
            state = True

        else:
            self._SavePinState  = 1
            value = self._ON_VALUE
            state = True

        self._loghandle.info('BinaryOut::Get %s port %s Status %s',self._NAME, self._HWID, value) 
        
        return {'VALUE':value, 'NAME':name, 'STATE':state} 
            
    def Update(self):
             
        return None
    
    def GetDirection(self):
        return self._DIRECTION
    
    def GetName(self):
        return self._NAME
        
    def GetMode(self):
        return self._MODE
    
class BinaryIn(object):
    '''
    classdocs
    '''
    def __init__(self, hwHandle, hwDevice, configuration):
        '''
        Constructor
        '''    
        self._hwHandle = hwHandle
        self._hwDevice = hwDevice
        self._config = configuration
        self._loghandle = loghandle()
        
        self.Setup()
        
    def Setup(self):
        
    #    self._SavePinState = ''
        
 
        if any(temp in self._hwDevice for temp in ['MCP23017','RASPBERRY']):
            ''' 
            Mandatory configuration Items
            '''
            try:
                self._NAME = self._config.get('NAME')
                self._HWID = int(self._config.get('HWID'))
                self._MODE = self._config.get('MODE','BINARY-IN')

            except:
                self._loghandle.critical('BinaryOut::Init Mandatory Parameter missing for Port %s',self._NAME)
                
            ''' 
            optional configuration Items
            '''
            self._DIRECTION = self._config.get('DIRECTION','IN')
            self._OFF_VALUE = self._config.get('OFF_VALUE','OFF')
            self._ON_VALUE = self._config.get('ON_VALUE','ON')
            
            '''
            Define class variables
            '''
            self._SavePinState = 0
            self._RestultAvailable = False
                
            '''
            configure port as Input
            '''
            self._hwHandle.ConfigIO(self._HWID,1)
                
            self._loghandle.info('BinaryOut::Init Configure Port %s HardwareID %s in Mode %s',self._NAME,self._HWID,self._MODE)

        else:
            self._loghandle.crittical('BinaryOut::Setup: Device not Supported')
            
        return True
    
    def Set(self):
        
        return None
 
            
    def Get(self):
        '''
        Returns current state of port in Dictionary
        VALUE: as defined in ON/OFF_VALUE
        STATE: True/False whether VALUE true or false
        '''
        value = ''
        name = self._NAME
        state = False
        
        tempState = self._hwHandle.ReadPin(self._HWID)
        
        if tempState == 0:
            self._SavePinState = tempState
            value = self._OFF_VALUE
            state = True

        else:
            self._SavePinState = tempState
            value = self._ON_VALUE
            state = True

        self._loghandle.info('BinaryIn::Get; Port %s Status %s',self._NAME, value) 
        
        return {'VALUE':value,'NAME':name,'STATE':state}  
            
    def Update(self):
        ''' 
        returns true in case port has changed polarity between Update calls
        will be changed after Get() method called
        '''
        
        update = False
        value = ''
        
        pinState = self._hwHandle.ReadPin(self._HWID)
        
        if  pinState != self._SavePinState:
          #  print "pin", pinState, self._SavePinState
            self._SavePinState = pinState
           # self._RestultAvailable = True
            update = True
            
        else:
          #  self._RestultAvailable = False
            update = False
            
            self._loghandle.debug('BinaryIn::Update; update available: port %s Port changed from %s to %s update %s', self._NAME, self._SavePinState, pinState, update)
             
        return update
    
    def GetDirection(self):
        return self._DIRECTION
    
    def GetName(self):
        return self._NAME
        
    def GetMode(self):
        return self._MODE
        
class TimerOut(object):
    '''
    classdocs
    '''
    def __init__(self, hwHandle, hwDevice, configuration):
        '''
        Constructor
        '''    
        self._hwHandle = hwHandle
        self._hwDevice = hwDevice
        self._config = configuration
        self._loghandle = loghandle()
        
        self.Setup()
        
    def Setup(self):
        
 #       self._SavePinState = ''
 
        if any(temp in self._hwDevice for temp in ['MCP23017','RASPBERRY']):
            ''' 
            Mandatory configuration Items
            '''
            try:
                self._NAME = self._config.get('NAME')
                self._HWID = int(self._config.get('HWID'))
                self._MODE = self._config.get('MODE','TIMER-OUT')

            except:
                self._loghandle.critical('BinaryOut::Init Mandatory Parameter missing for Port %s',self._NAME)
                
            ''' 
            optional configuration Items
            '''
            self._DIRECTION = self._config.get('DIRECTION','OUT')
            self._ON_VALUE = self._config.get('ON_VALUE','ON')
            self._OFF_VALUE = self._config.get('OFF_VALUE','OFF')
            self._PULS_LENGTH = float(self._config.get('PULS_LENGTH',2))
            self._POLARITY = self._config.get('POLARIY','ON')
            
            '''
            Define class variables
            '''
            self._SavePinState = ''
            self._T0 = time.time()
            self._T1 = 0.0
            self._TimerOutState = False
                
            '''
            configure port as Input
            '''
            self._hwHandle.ConfigIO(self._HWID,0)
                
            self._loghandle.info('BinaryOut::Init Configure Port %s HardwareID %s in Mode %s',self._NAME,self._HWID,self._MODE)

        else:
            self._loghandle.crittical('BinaryOut::Setup: Device not Supported')
            
        return True
    
    def Set(self, value,deltaT1=None):
        '''
        Set port is set; value as in ON_VALUE defined
        Timer will be started T0 set to actual time
        Optional: PULS_LENGTH can be redefined by setting deltaT1
        '''
        if deltaT1 != None:
            self._PULS_LENGTH = deltaT1
                
        if self._ON_VALUE in value:
            self._T0 = time.time()
            self._TimerOutState = True
            self._hwHandle.WritePin(self._HWID, 1)
            self._loghandle.info('VirtualPort::SetPushButton Counter: %s, start T0: %s, Puls Length: %s',self._TimerOutState, self._T0, self._PULS_LENGTH)  
        else:
            self._loghandle.error('VirtualPort::Set Command %s not found for port',value)  
    
        return True
    
    def Get(self):
        
        value = None
        puls_length = self._PULS_LENGTH
        deltaT1 = self._T1
        name = self._NAME
        state = False
        
        if self._hwHandle.ReadPin(self._HWID) == 0:
            self._SavePinState  = 0
            value = self._OFF_VALUE
            state = True
        else:
            self._SavePinState  = 1
            value = self._ON_VALUE
            state = True

        self._loghandle.info('TimerOut:Get; Port Name: %s, Porte Status: %s, DeltaT1 %s, Configured T1 %s',name, value, deltaT1, puls_length) 
        
        return {'VALUE':value, 'NAME':name, 'PULS_LENGTH': puls_length, 'DELTA_T1': deltaT1, 'STATE':state} 

    def Update(self):       
        
        state = None  
        
        if self._TimerOutState == True:

            self._T1 = self._PULS_LENGTH + self._T0

            if time.time() > self._T1:
                self._hwHandle.WritePin(self._HWID, 0) 
                self._TimerOutState = False
                state = True
                self._loghandle.info('VirtualPort::PushButton timed out Port %s', self._NAME)
            else:
                state = False
            
        return state            
    
    def GetDirection(self):
        return self._DIRECTION
    
    def GetName(self):
        return self._NAME
        
    def GetMode(self):
        return self._MODE
    
class TimerIn(object):
    '''
    classdocs
    '''
    def __init__(self, hwHandle, hwDevice, configuration):
        '''
        Constructor
        '''    
        self._hwHandle = hwHandle
        self._hwDevice = hwDevice
        self._config = configuration
        self._loghandle = loghandle()
        
        self.Setup()
        
    def Setup(self):
        
    #    self._SavePinState = ''
 
        if any(temp in self._hwDevice for temp in ['MCP23017','RASPBERRY']):
            ''' 
            Mandatory configuration Items
            '''
            try:
                self._NAME = self._config.get('NAME')
                self._HWID = int(self._config.get('HWID'))
                self._MODE = self._config.get('MODE','TIMER-IN')

            except:
                self._loghandle.critical('BinaryOut::Init Mandatory Parameter missing for Port %s',self._NAME)
                
            ''' 
            optional configuration Items
            '''
            self._DIRECTION = self._config.get('DIRECTION','IN')
            self._OFF_VALUE = self._config.get('OFF_VALUE','OFF')
            self._ON_VALUE = self._config.get('ON_VALUE','ON')
 
            '''
            Define class variables
            '''
            self._SavePinState = ''

            self._T0 = time.time()
            self._T1 = 0.0
            self._T2 = 0.0

            self._ResultAvailable = False
                
            '''
            configure port as Input
            '''
            self._hwHandle.ConfigIO(self._HWID,1)
                
            self._loghandle.info('BinaryOut::Init Configure Port %s HardwareID %s in Mode %s',self._NAME,self._HWID,self._MODE)

        else:
            self._loghandle.crittical('BinaryOut::Setup: Device not Supported')
            
        return True
    
    def Set(self, value):
      
        return None
    
    def Get(self):
        '''
        Returns current state of port in Dictionary
        VALUE: as defined in ON/OFF_VALUE
        STATE: True/False whether VALUE true or false
        '''
        value = ''
        deltaT1 = self._T1
        name = self._NAME
        state = self._ResultAvailable

        if self._hwHandle.ReadPin(self._HWID) == 0:
            self._SavePinState  = 0
            value = self._OFF_VALUE

        else:
            self._SavePinState  = 1
            value = self._ON_VALUE

        self._loghandle.info('BinaryOut::Get %s port %s Status %s',self._NAME, self._HWID, value) 
        
        message=json.dumps({
                "DELTA_T1": deltaT1,
                "VALUE": value,
                "RESULT": state
        })
        
        return {'VALUE':message, 'NAME':name, 'DELTA_T1': deltaT1, 'STATE':state} 
  #      return True      
    
    def Update(self):
        '''
        Returns True in case push button cycles is completed
        button pushed and released
        details returned by Get method
        '''

#        savedState = self._savedState
      #  resultDict = self.Get()
       # pinState = resultDict.get('State',None)
       
   #     print "Portname:",self.GetMode(), self.GetName()      
        pinState = self._hwHandle.ReadPin(self._HWID)
        update = False
    #    print "Pinstate", pinState
     #   print "SaveState", self._TimerInState

        '''
        was there a state change in the last period
        '''
        if pinState != self._SavePinState:
            '''
            was it a T0 or T2 event
            '''
     #       print "Debounce state change"
            self._SavePinState = pinState
            self._TimerInState = pinState
            if self._T0 == 0:
                ''' T0 event '''
                self._T0 = time.time()
               # print "T0 event", self._T0
                self._loghandle.info('VirtualPort::Update Timer-In button pressed T0-Timer Start at %s',self._T0)
                update = False
                self._ResultAvailable = False
            else:
                ''' T1 event '''
                self._T2 = time.time()
                update = True
                self._ResultAvailable = True
                '''Calculate time between events'''
                self._T1 = self._T2 - self._T0
                #self._T2 = int(self._T2)
              #  print "T1 event Time:", self._T2
                self._loghandle.info('VirtualPort::Update Timer-In button pressed T0: %s released T2: %s active for T1: %s seconds',self._T0, self._T2, self._T1)
                self._T0 = 0
        else:
            update = False
             
        return update           
    
    def GetDirection(self):
        return self._DIRECTION
    
    def GetName(self):
        return self._NAME
        
    def GetMode(self):
        return self._MODE
    
class PWM(object):
    '''
    classdocs
    '''
    def __init__(self, hwHandle, hwDevice, configuration):
        '''
        Constructor
        '''    
        self._hwHandle = hwHandle
        self._hwDevice = hwDevice
        self._config = configuration
        self._loghandle = loghandle()
        
        self.Setup()
        
    def Setup(self):
        
    #    self._SavePinState = ''
 
        if any(temp in self._hwDevice for temp in ['RASPBERRY']):
            ''' 
            Mandatory configuration Items
            '''
            try:
                self._NAME = self._config.get('NAME')
                self._HWID = int(self._config.get('HWID'))
                self._MODE = self._config.get('MODE','PWM')

            except:
                self._loghandle.critical('PWM::Init Mandatory Parameter missing for Port %s',self._NAME)
                
            ''' 
            optional configuration Items
            '''
            self._DIRECTION = self._config.get('DIRECTION','OUT')
            self._OFF_VALUE = self._config.get('OFF_VALUE','OFF')
            self._ON_VALUE = self._config.get('ON_VALUE','ON')
 
            '''
            Define class variables
            '''
            self._SavePinState = ''
            self._pwmState = False
 
                
            '''
            configure port as Input
            '''
            self._hwHandle.ConfigPWM(self._HWID) 
                
            self._loghandle.info('VPM_PWM::Init Configure Port %s HardwareID %s in Mode %s',self._NAME,self._HWID,self._MODE)

        else:
            self._loghandle.crittical('VPM_PWM::Setup: Device not Supported')
            
        return True
    
    def Set(self, value):
        
        try: 
            self._loghandle.info('VPM_PWM::SetPWM value write PWM %s write %s',self._NAME,value) 
            self._flashFrequency = float(value)
            self._hwHandle.WritePWM(self._HWID,value) 
            
        except ValueError:
         #   self._flashFrequency = int(2)
          #  self._t1 = time.clock()
            self._loghandle.error('VPM_PWM::SetPWM value error %s not supported',value) 
        return True
    
    def Get(self):
        '''
        Returns current state of port in Dictionary
        VALUE: as defined in ON/OFF_VALUE
        STATE: True/False whether VALUE true or false
        '''
        return {'VALUE':True,'NAME':self.GetName(),'STATE':True}      
    
    def Update(self):
  
        return True         
    
    def GetDirection(self):
        return self._DIRECTION
    
    def GetName(self):
        return self._NAME
        
    def GetMode(self):
        return self._MODE    
    
class S0(object):
    '''
    classdocs
    '''
    def __init__(self, hwHandle, hwDevice, configuration):
        '''
        Constructor
        '''    
        self._hwHandle = hwHandle
        self._hwDevice = hwDevice
        self._config = configuration
        self._loghandle = loghandle()
        
        self.Setup()
        
    def Setup(self):
        
    #    self._SavePinState = ''
 
        if any(temp in self._hwDevice for temp in ['MCP23017','RASPBERRY']):
            ''' 
            Mandatory configuration Items
            '''
            try:
                self._NAME = self._config.get('NAME')
                self._HWID = int(self._config.get('HWID'))
                self._MODE = self._config.get('MODE','S0')
                self._FACTOR = float(self._config.get('FACTOR','2000'))

            except:
                self._loghandle.critical('BinaryOut::Init Mandatory Parameter missing for Port %s',self._NAME)
                
            ''' 
            optional configuration Items
            '''
            self._DIRECTION = self._config.get('DIRECTION','IN')
            self._OFF_VALUE = self._config.get('OFF_VALUE','OFF')
            self._ON_VALUE = self._config.get('ON_VALUE','ON')
 
            '''
            Define class variables
            '''
            self._SavePinState = 0

            self._T0 = time.time()
            self._T1 = 0.0
            self._T2 = 0.0
            self._T3 = time.time()
            
            self._baseState = 0

            self._ResultAvailable = False
            
            self._watt = 0.0
            self._energySum = 0.0
            self._energyDelta = 0.0
            self._pulsCount = 0

            '''
            configure port as Input
            '''
            self._hwHandle.ConfigIO(self._HWID,1)
            self._SavePinState = self._hwHandle.ReadPin(self._HWID)
                
            self._loghandle.info('BinaryOut::Init Configure Port %s HardwareID %s in Mode %s',self._NAME,self._HWID,self._MODE)

        else:
            self._loghandle.crittical('BinaryOut::Setup: Device not Supported')
            
        return True
    
    def Set(self, value):
      
        return None
    
    def Get(self):
        '''
        Returns current state of port in Dictionary
        VALUE: as defined in ON/OFF_VALUE
        STATE: True/False whether VALUE true or false
        '''
        value = ''
        deltaT1 = self._T1
        name = self._NAME
        state = True
        
        self._loghandle.info('S0::Get Port %s Status %s',self._NAME, deltaT1) 
        
        message=json.dumps({
                "ENERGY": self._energySum,
                "ENERGYDELTA": self._energyDelta,
                "POWER": self._watt,
                "RESULT": state
        })
        
        return {'VALUE':message, 'NAME':name, 'STATE':state} 
  #      return True      
    
    def Update(self):
        '''
        Returns True in case push button cycles is completed
        button pushed and released
        details returned by Get method
        '''
        update = False
   #     factor = 2000
        
        if self._SavePinState > 1 and self._hwHandle.ReadPin(self._HWID) == 0:
     
            print "state1"
            print "SavePinState", self._SavePinState
            print "PinState", self._hwHandle.ReadPin(self._HWID)
            self._SavePinState = self._hwHandle.ReadPin(self._HWID)
            
            if self._T0 == 0:
                ''' 
                0 -> 1 transient  =T0
                '''
                print "T0: load current time"
                self._T0 = time.time()
    
            else:
                print "T2: measure time T2 -T0"
                self._T2 = time.time()
                self._T1 = self._T2 -self._T0
                print "T2", self._T2,"T0", self._T0
                print "delta T1:",self._T1
                self._T0 = time.time()
                print "T0new", self._T0
                self.Power()
                self.Energy()
                self._T2 = 0
                update = True
                print "SavePinState", self._SavePinState
                print "PinState", self._hwHandle.ReadPin(self._HWID)
#                watt = 1/factor*3600/self._T1*1000

             
        elif self._SavePinState == 0 and self._hwHandle.ReadPin(self._HWID) > 1:
            print "State2"
            print "SavePinState", self._SavePinState
            print "PinState", self._hwHandle.ReadPin(self._HWID)
            self._SavePinState = self._hwHandle.ReadPin(self._HWID)
            
        return update           
    
    def Power(self):
        self._watt = 1/self._FACTOR * 3600 / self._T1 * 1000
        self._pulsCount = self._pulsCount +1
        print "Watt", self._watt

        return self._watt
    
    def Energy(self):
        energyCurr = float(self._pulsCount / self._FACTOR)
        self._energyDelta = energyCurr - self._energySum 
        self._energySum = energyCurr
 #       print self._pulsCount / self._E_FACTOR
        print "Energy Current %f" % energyCurr, "EnergyDelata %f" % self._energyDelta, "EnergySum %f" % self._energySum, "Pulscounte", self._pulsCount
        return True
        
 #       return self._energySum
    
    def GetDirection(self):
        return self._DIRECTION
    
    def GetName(self):
        return self._NAME
        
    def GetMode(self):
        return self._MODE
    