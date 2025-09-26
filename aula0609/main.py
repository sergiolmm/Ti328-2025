import network
from time import sleep
from umqtt import MQTTClient

from machine import Pin
import time

led_y = Pin(27,Pin.OUT)
led_g = Pin(12,Pin.OUT)
led_r = Pin(14,Pin.OUT)

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
# define a callback para recever dados como assinante
def callback(topic, msg):
    global led_y
    global led_r
    global led_g
    print(f'{topic} send {msg}')
    try:
        msg_dec = json.loads(msg)
        if "led_y" in msg_dec:
            led_y.value(msg_dec["led_y"]) 
        if "led_g" in msg_dec:
            led_g.value(msg_dec["led_g"]) 
        if "led_r" in msg_dec:
            led_r.value(msg_dec["led_r"]) 
    
    except ValueError as e:
        print(f"erro ao decodificar {e}" )

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
    client.set_callback(callback)
    client.connect()
    print('Conectou ao Broker')
except OSError as e:
    print(f'Erro ao conectar {e}')
    sleep(3)
    machine.reset()
    
topic_sub = b'aula0509ns'

client.subscribe(topic_sub)

btn = Pin(4, Pin.IN, Pin.PULL_UP)
estado = False
# Initialize last_press_time for debouncing

last_press_time = 0


# Interrupt Service Routine (ISR) - this function runs when the interrupt is triggered
def button_handler(pin):
    global estado
    global client
    global last_press_time
    print('clicou')
    # Debounce: only process if enough time has passed since the last press
    # This helps prevent multiple triggers from a single physical button press
    current_time = time.ticks_ms()
    if (current_time - last_press_time) > 200: # 200ms debounce
        if not estado:
            msg= b'{"led_y" : 1, "led_r": 1, "led_g": 1}'
        else:
            msg= b'{"led_y" : 0, "led_r": 0, "led_g": 0}'
        estado = not estado
        client.publish(topic_sub, msg)
        last_press_time = current_time



# Attach the interrupt to the button pin
# Pin.IRQ_FALLING means trigger when the pin goes from HIGH to LOW (button pressed with pull-up)
btn.irq(trigger=Pin.IRQ_FALLING, handler=button_handler)


try:
    while True:
        try:
            #client.wait_msg()
            client.check_msg()
        except OSError as e:
            client.disconnect()
            print(f'{e}')
            sleep(3)
            client.connect()
            client.subscribe(topic_sub)
        '''
        if btn.value() == 0:
            print('Apertou')
            if not estado:
                msg= b'{"led_y" : 1, "led_r": 1, "led_g": 1}'
            else:
                msg= b'{"led_y" : 0, "led_r": 0, "led_g": 0}'
            estado = not estado
            client.publish(topic_sub, msg)
        '''    
        sleep(0.5)    
        

except KeyboardInterrupt:
    print('parou')
    client.disconnect()
    
    
    
'''

'''
    
    
    
    
    
    







