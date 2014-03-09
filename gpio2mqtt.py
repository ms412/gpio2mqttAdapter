#!/usr/bin/python
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

__app__ = "Gpio2Mqtt Adapter"
__VERSION__ = "0.4"
__DATE__ = "01.12.2014"
__author__ = "Markus Schiesser"
__contact__ = "M.Schiesser@gmail.com"
__copyright__ = "Copyright (C) 2014 Markus Schiesser"
__license__ = 'GPL v3'

import os
import sys
import time
import Queue



from config import config
from logAdapter import loghandle
from mqttAdapter import mqttclient
from vhm import vhm
from daemon import daemon

class Manager(daemon):
    
    def __init__(self,configfile):
        
        self._mqttQueue = Queue.Queue()

        self._configfile = configfile
        self._configAll = config()
        print configfile
        self._configAll.Open(self._configfile)
        self._configGeneral = config(self._configAll.subsection('Config','General'))
#        print "TesT",self._configALL
        self._pidfile = str(self._configGeneral.get(0,'PIDFILE','/var/run/gpio2mqtt.pid'))
        self._loghandle = None
        
        daemon.__init__(self, self._pidfile)  
        
    def logging_start(self):

        logfile = str(self._configGeneral.get(0,'LOGFILE','/var/log/gpio2mqtt.log'))
        logmode = str(self._configGeneral.get(0,'LOGMODE','DEBUG'))
        
        self._loghandle=loghandle()  
        self._loghandle.open(logfile,logmode)
        
        self._loghandle.info('Starting Gpio2Mqtt Adapter Version: %s %s',  __VERSION__,__DATE__)
        self._loghandle.debug('Logfile: %s Logmode: %s', logfile, logmode)
        self._loghandle.info('Read Config from File %s:',self._configfile)
        
    def mqtt_start(self):
        configMqtt = self._configAll.subsection('Config', 'Broker')
        self._mqttThread = mqttclient(configMqtt,self._mqttQueue)
        self._loghandle.debug('Start MqttClient with config: %s ', configMqtt)
        self._mqttThread.start()
      
    def vhm_start(self):
        configVHM = self._configAll.subsection('Config', 'DEVICE[0-9]')
        self._loghandle.debug('Start VHM manager with config: %s ', configVHM)
        print "vhm",configVHM
        self._vhm = vhm(configVHM)
        
    def FilterMqtt2VHM(self, mqttMsg):
        """
        Filter for Mqtt Objects and transforms them to VHM valid data
        """
        #self.log.debug('FilterMqtt2VHM: %s', mqttMsg)
        resultDict ={}
        #print(mqttMsg.topic+" "+str(mqttMsg.qos)+" "+str(mqttMsg.payload))
        topic = mqttMsg.topic
        cmd = mqttMsg.payload 
        list_topic = topic.split("/")
        resultDict.update({'DEVICE_NAME':list_topic[-2]})
        resultDict.update({'PORT_NAME':list_topic[-1]})
        resultDict.update({'PORT_STATE':cmd})
        #self.log.debug('FilterOutput: %s', resultDict)
        return resultDict
        
    def FilterVHM2MQTT(self, vhmDict):
        """ 
        Filter transforms informations from VHM to MQTT
        """
        self._loghandle.debug('Manager::FilterVHM2MQTT Message %s', vhmDict)
        device_name = vhmDict.get('DEVICE_NAME','None')
        port_name = vhmDict.get('PORT_NAME','None')
        port_state = str(vhmDict.get('PORT_VALUE','None'))
        
        mqtt_sub_ch = device_name + '/' + port_name
        
        return {'mqtt_msg':port_state, 'mqtt_sub_ch':mqtt_sub_ch}
    
    def pollIOUpdate(self):
        
        vhmList = self._vhm.Update()
  #      print "VHMDict Leng:", len(data)
        if 0 != len(vhmList):
            #for vhmDict in self._vhm.Update():
            for vhmDict in vhmList:
                print 'VHMDict: ',vhmDict
                resultDict = self.FilterVHM2MQTT(vhmDict)
                mqtt_sub_ch = resultDict.get('mqtt_sub_ch')
                mqtt_msg = resultDict.get('mqtt_msg')
                self._loghandle.info('Manager::pollIOUpdate GPIO Updates and Publish to Mqtt; Channel: %s, message: %s',mqtt_sub_ch, mqtt_msg)
                self._mqttThread.mqtt_send(resultDict)
        #else:
         #   self._loghandle.error('Manager::sendUpdateMsg no Data available')
                
    def pollMqttUpdate(self):
  #      self.log.debug('Getmessage')
        self._loghandle.info('Manager::pollMqttUpdate, Number of MQTT messages available: %s',self._mqttQueue.qsize())
        
        while self._mqttQueue.qsize():
            mqttMsg = self._mqttQueue.get(True, 5)
            vhmDict = self.FilterMqtt2VHM(mqttMsg)
            device_name = vhmDict.get('DEVICE_NAME','None')
            port_name = vhmDict.get('PORT_NAME','None')
            port_state = vhmDict.get('PORT_STATE','None')
            
#            print " write to VHM", channel, name, state
            if 'ADMINISTRATION' in port_name and 'SYNC' in port_state: 
                self._loghandle.info('Manager::pollMqttUpdate Administrative Message Received: %s Request: %s',port_name,port_state)
                self._vhm.RequestSync()          
            else:
                self._loghandle.info('Manager::pollMqttUpdate Received message from Mqtt Channel: %s Name: %s State: %s',device_name,port_name,port_state)
                self._vhm.Write(device_name,port_name,port_state)
            
        return
    
    def ThreadMonitor(self):
        result = True
        
        if self._mqttThread.isAlive()== False:
            result = False
            self._loghandle.critical('Manager::ThreadMonitor Mqtt Thread no responding!')
            
        if self._vhm.ThreadMonitor() == False:
            result = False
            self._loghandle.critical('Manager::ThreadMonitor VHM Threads not responding!')

  #     self._loghandle.debug('Manager::ThreadMonitor Threads OK: %s',result)
        return result
    
    def run(self):
        """
        Entry point, initiates components and loops forever...
        """
        
        self.logging_start()
        self.mqtt_start()
        self.vhm_start()

        while True:
        #    self._mqttThread.mqtt_send({'msg':'ALIVE', 'channel':'/OPENHAB'})
            self.pollIOUpdate()
            
            if self.ThreadMonitor() == False:
                self._loghandle.critical('Manager::Run Thread died!')
                
            if self._mqttQueue.qsize() > 0:
                #msg = self._mqttQueue.get()
     #           print "Received MQQTT Data"
                self.pollMqttUpdate()     
    
            time.sleep(1)
            
        self._loghandle.critical('Manager::Run Thread terminated!')
        


#def main():
if __name__ == "__main__":
    
    print "main"

    if len(sys.argv) == 3:
        configfile = sys.argv[2]
    else:
        configfile = '/etc/gpio2mqtt/config.yaml'
    
    daemon = Manager(configfile)
    if len(sys.argv) >= 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        elif 'run' == sys.argv[1]:
            print "RUN"
            daemon.run()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)