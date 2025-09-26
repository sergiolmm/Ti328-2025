from machine import Pin
from time import sleep


pwd = input("Digite a senha")
print(pwd)

led_y = Pin(27,Pin.OUT)
led_g = Pin(12,Pin.OUT)
led_r = Pin(14,Pin.OUT)


try:
    while True:
        led_y.value(1)
        led_g.value(1)
        led_r.value(1)
        sleep(0.5)
        led_y.value(0)
        led_g.value(0)
        led_r.value(0)
        sleep(0.5)

except KeyboardInterrupt:
    print('parou')
finally:
    led_y.value(0)
    led_g.value(0)
    led_r.value(0)