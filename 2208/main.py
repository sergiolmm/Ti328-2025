# primeiro projeto em python para esp32

import network

SSID = "D-Link_DIR-615"
pwd = ''

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

redes = wlan.scan()
# listo as redes disponiveis
for rede in redes:
    ssid = rede[0].decode()
    rssi = rede[3]
    print(f'{ssid} ({rssi} dBm)')

print("Tentando conectar a rede WIFI")
while not wlan.isconnected():
    wlan.connect(SSID, pwd)
    print(".", end="")
    
print(wlan.ipconfig())    