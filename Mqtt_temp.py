import network
from time import sleep
from simple import MQTTClient

from machine import Pin
import time
from machine import Timer
from machine import ADC

ledv = Pin(12, Pin.OUT)
ledv.value(0)
ledy = Pin(14, Pin.OUT)
ledy.value(0)
ledg = Pin(27, Pin.OUT)
ledg.value(0)
pwd_file = open('pwd.txt', 'r')
#print(pwd_file.readline())
pwd1 = pwd_file.readline()

rede = network.WLAN(network.STA_IF)
rede.active(True)

rede.connect("iPhone de Sergio", pwd1)
while not rede.isconnected():
    print('.', end='')
    sleep(1)
    

print(f'Conectado ao ip {rede.ifconfig()[0]}')

# parametrizar o mqtt client e sua conexao com Broker Hivemq
mqtt_server = b'73a3246b4410491692df6b23c34b84cc.s1.eu.hivemq.cloud'
port = 8883
user = b'noturno'
pwd = b'Cotuca25'

import machine
import ubinascii
client_id = ubinascii.hexlify(machine.unique_id())

import json
 

def trataMsg(topic, msg):
    print(f'{topic} -> {msg}')
    try:
        msg_dec = json.loads(msg)
        if "red" in msg_dec:
            ledv.value(msg_dec["red"])
        if "green" in msg_dec:
            ledg.value(msg_dec["green"])   
        if "yellow" in msg_dec:
            ledy.value(msg_dec["yellow"])
                
    except:
        print('erro')
try:
    client = MQTTClient(
        client_id,
        mqtt_server,
        port = port,
        user = user,
        password = pwd,
        keepalive = 30,
        ssl = True,
        ssl_params = {"server_hostname": mqtt_server}       
        )
    client.set_callback(trataMsg)
    client.connect()
    print('Conectou ao Broker')
except OSError as e:
    print(f'Erro ao conectar {e}')
    sleep(3)
    machine.reset()

def publica(timer):
    global topic_sub
    global msg
    client.publish(topic_sub, msg)



power = Pin(26, Pin.OUT)  # solucao do hardware professor
power.value(1)		      # nao utilizar (copiar)		

# Define the ADC pin connected to LM35 output
lm35_pin = Pin(35)  # Example: Using GPIO32

# Create an ADC object
adc = ADC(lm35_pin)
adc.atten(ADC.ATTN_11DB) # Set attenuation for full range (0-3.3V)
cnt = 0
media = []

timer0 = Timer(0)
timer0.init(mode=Timer.PERIODIC, period= 3000, callback=publica)


topic_sub = b'media'
msg = ""
client.subscribe(topic_sub)
try:
    while True:
        try:
            #client.wait_msg()
            msg = b'teste'
           
            client.check_msg()
            
            # Read raw ADC value
            raw_value = adc.read()
            # Convert raw value to voltage (assuming 12-bit ADC and 3.3V reference)
            voltage = (raw_value / 4095) * 3.3

            # Convert voltage to Celsius temperature
            temperature_celsius = voltage / 0.01
            media.append(temperature_celsius)
            v_media = sum(media)/len(media)
            # Print the temperature
            print(f"Raw ADC: {raw_value}, Voltage: {voltage:.2f}V, Temperature: {temperature_celsius:.2f}°C Media {v_media:.2f}°C")
            if len(media) > 20:
                media.clear()
            
        except OSError as e:
            client.disconnect()
            print(f'{e}')
            sleep(3)
            client.connect()
            client.subscribe(topic_sub)
        
        sleep(0.3)    
        

except KeyboardInterrupt:
    print('parou')
    client.disconnect()