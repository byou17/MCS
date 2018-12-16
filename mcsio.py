#!/usr/bin/python
import sys
import Adafruit_DHT
import time
import httplib
import urllib
import json
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(24,GPIO.IN,pull_up_down=GPIO.PUD_UP)

deviceId = "Dt8VsB0P"
deviceKey = "OFh3Pt6RGLbDYLJS"
 
def post_to_mcs(payload): 
        headers = {"Content-type": "application/json", "deviceKey": deviceKey} 
        not_connected = 1 
        while (not_connected):
                try:
                        conn = httplib.HTTPConnection("api.mediatek.com:80")
                        conn.connect() 
                        not_connected = 0 
                except (httplib.HTTPException, socket.error) as ex: 
                        print "Error: %s" % ex
                        time.sleep(10)
                         # sleep 10 seconds 
        conn.request("POST", "/mcs/v2/devices/" + deviceId + "/datapoints", json.dumps(payload), headers)
        response = conn.getresponse() 
        print( response.status, response.reason, json.dumps(payload), time.strftime("%c")) 
        data = response.read() 
        conn.close() 



# Parse command line parameters.
sensor_args = { '11': Adafruit_DHT.DHT11,
                '22': Adafruit_DHT.DHT22,
                '2302': Adafruit_DHT.AM2302 }

if len(sys.argv) == 3 and sys.argv[1] in sensor_args:
    sensor = sensor_args[sys.argv[1]]
    pin = sys.argv[2]
else:
    print('Usage: sudo ./Adafruit_DHT.py [11|22|2302] <GPIO pin number>')
    print('Example: sudo ./Adafruit_DHT.py 2302 4 - Read from an AM2302 connected to GPIO pin #4')
    sys.exit(1)

# Try to grab a sensor reading.  Use the read_retry method which will retry up
# to 15 times to get a sensor reading (waiting 2 seconds between each retry).
while True:
        B,A = Adafruit_DHT.read_retry(sensor, pin)

        switch = GPIO.input(24)
        if(switch == 1):
                print("Button pressed")

        else:
                print("Button released")
# Un-comment the link below to convert the temperature to Fahrenheit.
# temperature = temperature * 9/5.0 + 32

# Note that sometimes you won't get a reading and
# the results will be null (because Linux can't
# guarantee the timing of calls to read the sensor).
# If this happens try again!
        if A is not None and B is not None:
                print('Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(A,B))

                payload = {"datapoints":[{"dataChnId":"B","values":{"value":B}},
                {"dataChnId":"A","values":{"value":A}},
                {"dataChnId":"switch","values":{"value":switch}}]} 
                post_to_mcs(payload)
                time.sleep(1) 
        else:
                 print('Failed to get reading. Try again!')
                 sys.exit(1)

