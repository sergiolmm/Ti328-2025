from machine import ADC, Pin
import time

leds = [Pin(12, Pin.OUT),
Pin(14, Pin.OUT),Pin(27, Pin.OUT)]

for x in range(len(leds)):
    leds[x].value(1)
    time.sleep(1)
    leds[x].value(0)
    time.sleep(1)
    

power = Pin(26, Pin.OUT)  # solucao do hardware professor
power.value(1)		      # nao utilizar (copiar)		

# Define the ADC pin connected to LM35 output
lm35_pin = Pin(35)  # Example: Using GPIO32

# Create an ADC object
adc = ADC(lm35_pin)
adc.atten(ADC.ATTN_11DB) # Set attenuation for full range (0-3.3V)
cnt = 0
media = []
while True:
    leds[cnt%3].value(1)
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
    
    time.sleep(3) # Read every 2 seconds
    print(f'valor {cnt%3}')
    leds[cnt%3].value(0)
    cnt +=1
    if len(media) > 20:
        media.clear()