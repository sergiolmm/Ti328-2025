from machine import ADC, Pin
import time

'''
       ##########
      #         #
       # A B C #
        #     #
         ####
        A - VCC (5v)
        b - pino 35 ou 36
        c - GND (0v)        
        '''

# Define the ADC pin connected to LM35 output
lm35_pin = Pin(35)  # Example: Using GPIO32

# Create an ADC object
adc = ADC(lm35_pin)
adc.atten(ADC.ATTN_11DB) # Set attenuation for full range (0-3.3V)

while True:
    # Read raw ADC value
    raw_value = adc.read()

    # Convert raw value to voltage (assuming 12-bit ADC and 3.3V reference)
    voltage = (raw_value / 4095) * 3.3

    # Convert voltage to Celsius temperature
    temperature_celsius = voltage / 0.01

    # Print the temperature
    print(f"Raw ADC: {raw_value}, Voltage: {voltage:.2f}V, Temperature: {temperature_celsius:.2f}°C")

    time.sleep(2) # Read every 2 seconds
