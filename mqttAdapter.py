
import sys
import os
import time
import Queue
import threading

from config import config
from wrapper_log import loghandle

try:
    import paho.mqtt.client as mqtt
except:
    import paho as mqtt
    print "start local mqtt driver"

class mqttclient(threading.Thread):
    def __init__(self, configuration, queue):
        
        threading.Thread.__init__(self)
        
        self._config = config(configuration)
        self._receiveQueue = queue
        self._sendQueue = Queue.Queue() 
        
        self._loghandle = loghandle()

        self._host = str(self._config.get(0,'MQTT_HOST','localhost'))
        self._port = int(self._config.get(0,'MQTT_PORT',1883))
#        tempChannel = self._config.get(0,'MQTT_CHANNEL','/OPENHAB') +'/'+'#'
        self._mqtt_sub_ch = str(self._config.get(0,'MQTT_SUB_CH','/RASPBERRY02') +'/'+'#')
        self._mqtt_pub_ch = str(self._config.get(0,'MQTT_PUB_CH','/OPENHAB02'))
 #       self._channel = str(tempChannel)
        
        self._loghandle.info('MqttWrapper::Init Start Mqtt Client Thread at host: %s; Port: %s; Subscribe Ch.: %s; Publish Ch.: %s;',self._host, self._port, self._mqtt_sub_ch, self._mqtt_pub_ch  )
        
        self._mqttc = mqtt.Client(str(os.getpid()))
        self._mqttc.on_message = self.mqtt_on_message
        self._mqttc.on_connect = self.mqtt_on_connect
        self._mqttc.on_publish = self.mqtt_on_publish
        self._mqttc.on_subscribe = self.mqtt_on_subscribe
        self._mqttc.on_disconnect = self.mqtt_on_disconnect
        
    def __del__(self):
        '''
        delets the mqtt wrapper object
        '''
        self._loghandle.debug('MqttWrapper::Stop Mqtt Thread')
        
    def mqtt_on_connect(self, mqttc, obj, rc):
        self._loghandle.debug('MqttWrapper::Connect connected rc: %s',str(rc))
        
    def mqtt_on_disconnect(self,result_code):
        self._loghandle.error('MqttWrapper::Diconnect Mqtt got dissconnected with error code: %s',result_code)
        if result_code == 0:
            self._loghandle.critical('MqttWrapper::Disconnect Mqtt got dissconnected System shut down',result_code)
           # print "Shuting down System"
        else:
            time.sleep(5)
            self.run()

    def mqtt_on_message(self, mqttc, obj, msg):
  #      print('Print ifnoe: ',msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
        self._loghandle.info('MqttWrapper::Message Received channel: %s message: %s', str(msg.topic), str(msg.payload))
        self._receiveQueue.put(msg)

    def mqtt_on_publish(self, mqttc, obj, mid):
 #       print("mid: "+str(mid))
        return 0

    def mqtt_on_subscribe(self, mqttc, obj, mid, granted_qos):
      #  print("Subscribed: "+str(mid)+" "+str(granted_qos))
        self._loghandle.debug('MqttWrapper::Subscribed to Channel with success')

    def mqtt_on_log(self, mqttc, obj, level, string):
      #  print(string)
        self._loghandle.error('MqttWrapper::Log Mqtt Logmessage: %s',string)
        
    def mqtt_send(self,msgDict):
        self._sendQueue.put(msgDict)
        
    def mqtt_publish(self,msg,channel=None):
        
        if channel is None:
            channel = self._mqtt_pub_ch
            
        channel = str(self._mqtt_pub_ch +'/' + channel)
        
        self._loghandle.info('MqttWrapper::Publish to Channel: %s Message: %s',channel, msg)
        self._mqttc.publish(channel, msg)

        return True

    def run(self):
        self._mqttc.connect(self._host, self._port, 60)

        self._mqttc.subscribe(self._mqtt_sub_ch, 0)

        rc = 0
        while rc == 0:
          #  time.sleep(5)
    #        print "mqtt loop"
            rc = self._mqttc.loop()
            while self._sendQueue.qsize():
                self._loghandle.debug('MqttWrapper::Run Messages to be send available %s:',self._sendQueue.qsize())
                (msgDict)=self._sendQueue.get()
                self.mqtt_publish(msgDict.get('mqtt_msg'), msgDict.get('mqtt_sub_ch',None))

        self._loghandle.critical('MqttWrapper::Run Mqtt Thread malfunction',rc)
        return rc

