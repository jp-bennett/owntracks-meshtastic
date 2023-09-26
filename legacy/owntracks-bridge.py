import paho.mqtt.client as mqttClient
import time
import json

tid_table = {

"123456789": ("Radio1", "R1"),
"0123456789": ("Radio2", "R2")
}

def on_message(client, userdata, message):
    msh_object = json.loads(message.payload)
    if (msh_object["type"] == "position" and msh_object["payload"]["latitude_i"] != 0):
        own_object = json.loads('{"_type":"location", "bs":0}')
        if ("altitude" in msh_object["payload"]):
            own_object["alt"] = msh_object["payload"]["altitude"]
        own_object["lat"] = msh_object["payload"]["latitude_i"]/10000000
        own_object["lon"] = msh_object["payload"]["longitude_i"]/10000000
        own_object["tst"] = msh_object["timestamp"]
        if ("time" in msh_object["payload"]):
            own_object["created_at"] = msh_object["payload"]["time"]
        else:
            own_object["created_at"] = msh_object["timestamp"]
        if (str(msh_object["from"]) in tid_table):
            own_object["tid"] = tid_table[str(msh_object["from"])][1]
            client.publish("owntracks/user/" + tid_table[str(msh_object["from"])][0], json.dumps(own_object))
            print("owntracks/user/" + tid_table[str(msh_object["from"])][0])
            print(json.dumps(own_object))
        else:
            print("unknown FROM:" + json.dumps(msh_object))

def on_connect(client, userdata, flags, rc):

    if rc == 0:

        print("Connected to broker")

        global Connected                #Use global variable
        Connected = True                #Signal connection

    else:

        print("Connection failed")




Connected = False #global variable for the state of the connection

broker_address= "127.0.0.1"
port = 1883


client = mqttClient.Client("Python")               #create new instance
client.on_connect= on_connect                      #attach function to callback
client.on_message= on_message                      #attach function to callback


client.connect(broker_address, port=port)  #connect to broker
client.loop_start()                        #start the loop

while Connected != True:    #Wait for connection
    time.sleep(0.1)

client.subscribe("msh/+/json/#")

try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("exiting")
    client.disconnect()
    client.loop_stop()
