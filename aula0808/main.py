# primeiro projeto em python para esp32

import network

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

redes = wlan.scan()

for rede in redes:
    ssid = rede[0].decode()
    rssi = rede[3]
    print(f'{ssid} ({rssi} dBm)')
