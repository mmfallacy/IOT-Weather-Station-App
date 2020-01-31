import os,sys
from flask import Flask,render_template,session,redirect,url_for,request,jsonify
import requests
from datetime import datetime
import paho.mqtt.client as mqtt
from flask_socketio import SocketIO,emit
SESSION_SECRET_KEY = '99244c4975fa103866da48ae'
SERVER_PORT = 35223
DEBUG_MODE=False

## GET LOCATION BASED ON SERVER IP
response = requests.get("http://ip-api.com/json/"+requests.get('https://api.ipify.org').text)
LOCATION = response.json()

BROKER_URL = "tailor.cloudmqtt.com"
BROKER_USR = "fpbyprsg"
BROKER_PWD = "tDaZCwDn1M4T"
BROKER_PORT = 12129

DATA = {
    "tempC": 0, #Temperature in Celsius
    "tempF": 0, #Temperature in Fahrenheit
    "wind_spd": 0, #Wind Speed
    "wind_dir": 0, #Wind Direction ( in cw )
    "hum": 0, #Humidity ( Rh )
    "press": 0, #Pressure ( bar )
    "precip": 0  #Precipitation ( mm )
}

DATA_LOG ={
    "tempC": [{"data":"0","time":"00:00:00"}],
    "tempF": [{"data":"0","time":"00:00:00"}],
    "wind_spd":  [{"data":"0","time":"00:00:00"}],
    "wind_dir": [{"data":"0","time":"00:00:00"}],
    "hum":  [{"data":"0","time":"00:00:00"}],
    "press":  [{"data":"0","time":"00:00:00"}],
    "precip":  [{"data":"0","time":"00:00:00"}]
}

app = Flask(__name__)
app.secret_key = SESSION_SECRET_KEY
socket = SocketIO(app)
Client = mqtt.Client("IoT Web App")

def on_connect(client, userdata, flags, rc):
    print("Connected: " +str(rc))
    Client.subscribe("data/tempC")
    Client.subscribe("data/tempF")
    Client.subscribe("data/hum")
    Client.subscribe("data/press")
    Client.subscribe("data/precip")
    Client.subscribe("data/wind_spd")
    Client.subscribe("data/wind_dir")

def on_message(client, userdata, message):
    try:
        _value = message.payload.decode()
        _topic = message.topic.split("/")[1]
        raw_time = datetime.now()
        formatted_time = raw_time.strftime("%H:%M:%S")
        if len(DATA_LOG[_topic]) >=10:
            DATA_LOG[_topic].pop(0)
            DATA_LOG["time"].pop(0)
        DATA_LOG[_topic].append({"data":_value,"time":formatted_time})
        DATA[_topic]=_value
        print("Updating Web App: TOPIC: " + _topic +" with a value of " + _value)
        socket.emit("0x5Df9eBcFB2D0f3315d03Ac112104b9023C409dc1",data={"data":(_topic,_value),"time":formatted_time},namespace="/14yhtZxLNp6ekZAgmEmPJqEKUP2VtUxQK6")
    except Exception  as e:
        print(e)
Client.on_connect = on_connect
Client.on_message = on_message

CURRENT_DIRECTORY = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)

@app.route("/")
def index():
    return render_template("overview.gz", xpage="overview", **DATA, loc=[LOCATION["city"],LOCATION["regionName"],LOCATION["country"]])  

@app.route("/details")
def details():
    return render_template("details.gz", xpage="details", tempC = DATA["tempC"],DATA_LOG = DATA_LOG, loc=[LOCATION["city"],LOCATION["regionName"],LOCATION["country"]])  

@socket.on('connect', namespace="/14yhtZxLNp6ekZAgmEmPJqEKUP2VtUxQK6")
def handle_connect():
    print("Web app socket Connected!")

if __name__=="__main__": 
    Client.username_pw_set(BROKER_USR, BROKER_PWD)
    Client.connect(BROKER_URL,port=BROKER_PORT)
    if(not DEBUG_MODE):
        Client.loop_start()

    socket.run(app,"127.0.0.1",SERVER_PORT, debug=DEBUG_MODE)