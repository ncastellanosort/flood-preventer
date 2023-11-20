from hcsr04 import HCSR04
from ssd1306 import SSD1306_I2C
from machine import Pin as pin, PWM, I2C, Timer
import network, time
from umqtt.simple import MQTTClient
import random
import urequests, ujson


temporiza = Timer(0)                    
prev_weather = 0

i2c = I2C(0,sda=pin(2),scl=pin(5),freq=40000)
oled = SSD1306_I2C(128,64,i2c)
sensor = HCSR04(trigger_pin=18, echo_pin=19, echo_timeout_us=5000)
buzzer = PWM(pin(15))
buzzer.duty_u16(0)


MQTT_CLIENT_ID = ""

MQTT_BROKER    = "broker.hivemq.com" # El broker
MQTT_USER      = ""
MQTT_PASSWORD  = ""
topic_pub     = "nicolas/proyecto" # Eltopic donde vas a publicar
topic_sub      = 'nicolas/proyecto'


def conectar(red, contra):
    global mired
    
    mired = network.WLAN(network.STA_IF)
    
    if not mired.isconnected():
        mired.active(True)
        mired.connect(red, contra)
        print(f'Conectando a la red {red} ...')
        timeout = time.time()
        
        while not mired.isconnected():
            if (time.ticks_diff (time.time(), timeout) > 10):
                return False
            
    return True

if conectar('EYE3 2.4G', 'Castellanos2023Ort'):
    print('Conexion exitosa!') 
    
    # ver datos del clima
    uri = 'https://api.openweathermap.org/data/2.5/weather?q=Arauca&appid=84c3b570d602a28aa69e9796925026a1&units=metric&lang=es'

    respuesta = urequests.get(uri)

    datos = respuesta.json()
    
    hay_nubes = datos['weather'][0]['main']
    descripcionNubes = datos['weather'][0]['description']
    nubosidad = datos['clouds']['all']
    velocidadViento = datos['wind']['speed']
    humedadClima = datos['main']['humidity']
    
    

    # print(datos)
    print(f'\nEstado del clima: {hay_nubes}')
    print(f'Descripcion del clima: {descripcionNubes}')
    print(f'Nubosidad: {nubosidad} %')
    print(f'Velocidad del viento: {velocidadViento} km/h')
    print(f'Humedad: {humedadClima} %\n')

    respuesta.close()
    # hasta aca
 

    def sub_cb(topic, msg):
        print(f"llego el topic: {topic} con el valor {msg}")


    print("Connecting to MQTT server... ", end="")
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, user=MQTT_USER, password=MQTT_PASSWORD)

    client.set_callback(sub_cb)

    client.connect()

    client.subscribe(topic_sub)

    # print(f'Connected to {MQTT_BROKER} MQTT broker, subscribed to {topic_sub} topic')
    print("Connected!")
    prev_weather = ""
    
    def oledMostrar():
        oled.text(f'ALERTA', 2, 20, 1)
        oled.show()
        oled.text(f'ALERTA', 2, 20, 0)
        oled.show()
        oled.text(f'ALERTA', 50, 40, 1)
        oled.show()
        oled.text(f'ALERTA', 50, 40, 0)
        oled.show()
        oled.text(f'ALERTA', 30, 60, 1)
        oled.show()
        oled.text(f'ALERTA', 30, 60, 0)
        oled.show()

    def alarmaYmqttmssgs():

        x = 0 
        while x < 25:
            buzzer.duty_u16(32767)
            
            # print('ALERTA')
            
            def sub_cb(topic, msg):
                print(f"llego el topic: {topic} con el valor {msg}")
            

            def desborde (Timer):   
                global prev_weather
        
                numRand = str(random.randint(1,100))
                valor = str(f"ALERTA DE POSIBLE INUNDACION {numRand}")
    
                message = valor
                if message != prev_weather:
                    # print(f"valor publicado en el topic {topic_pub}: {message}  ")
                    client.publish("nicolas/proyecto", message)
                prev_weather = message


            temporiza.init(period=1000,mode=Timer.PERIODIC,callback=desborde)
            
            randomX1 = random.randint(3,110)
            randomX2 = random.randint(3,110)
            randomX3 = random.randint(3,110)
            
            
            randomY1 = random.randint(3,56)
            randomY2 = random.randint(3,56)
            randomY3 = random.randint(3,56)
            
            time.sleep(0.1)
            buzzer.freq(2637)
            oled.text(f'ALERTA', randomX1, randomY1, 1)
            oled.show()
            oled.text(f'ALERTA', randomX1, randomY1, 0)
            buzzer.freq(1568)
            
            time.sleep(0.1)
            buzzer.freq(2637)
            oled.text(f'ALERTA', randomX2, randomY2, 1)
            oled.show()
            oled.text(f'ALERTA', randomX2, randomY2, 0)
            buzzer.freq(1568)
            
            time.sleep(0.1)
            buzzer.freq(2637)
            oled.text(f'ALERTA', randomX3, randomY3, 1)
            oled.show()
            oled.text(f'ALERTA', randomX3, randomY3, 0)
            buzzer.freq(1568)
            
            x += 1
            
        buzzer.duty_u16(0)
        oled.poweroff()
    
    
    while True:
        
        distance = round(sensor.distance_cm(), 1)
        # print('Distancia del nivel del agua:', distance, 'cm')
        
        if distance > 9:
            oled.text(f'Alerta a 3m', 17, 28, 1)
            oled.text(f'Distancia agua:', 2, 42, 1)
            oled.text(f'{distance} m', 2, 52, 1)
            oled.show()
            oled.text(f'Distancia agua:', 2, 42, 0)
            oled.text(f'{distance} m', 2, 52, 0)
            oled.text(f'Alerta a 3m', 17, 28, 0)
        
        elif distance > 6.3 and distance < 8.1:
            oled.text(f'-NIVEL DE AGUA-', 2, 28, 1)
            oled.text(f'Normal', 17, 42, 1)
            oled.show()
            oled.text(f'Normal', 17, 42, 0)
            oled.text(f'*NIVEL DE AGUA*', 2, 28, 0)
        
        elif distance > 4.1 and distance < 6.2:
            oled.text(f'-NIVEL DE AGUA-', 2, 28, 1)
            oled.text(f'Creciente', 17, 42, 1)
            oled.show()
            oled.text(f'Creciente', 17, 42, 0)
            oled.text(f'*NIVEL DE AGUA*', 2, 28, 0)
            
            
        elif distance > 3.5 and distance < 4:
            oled.text(f'-NIVEL DE AGUA-', 2, 28, 1)
            oled.text(f'Peligro', 17, 42, 1)
            oled.show()
            oled.text(f'Peligro', 17, 42, 0)
            oled.text(f'*NIVEL DE AGUA*', 2, 28, 0)

        
        # Peligro Total y suena la alarma
        elif distance > 2.9 and distance < 3.1:
            alarmaYmqttmssgs()

        
        
    