from hcsr04 import HCSR04
from ssd1306 import SSD1306_I2C
from machine import Pin as pin, PWM, I2C, Timer
import network, urequests, time
# import ufirebase as firebase
from umqtt.simple import MQTTClient
import random


temporiza = Timer(0)                    
prev_weather = 0

i2c = I2C(0,sda=pin(2),scl=pin(5),freq=40000)
oled = SSD1306_I2C(128,64,i2c)
sensor = HCSR04(trigger_pin=18, echo_pin=19, echo_timeout_us=5000)
buzzer = PWM(pin(15))


MQTT_CLIENT_ID = ""

MQTT_BROKER    = "broker.hivemq.com" # El broker
MQTT_USER      = ""
MQTT_PASSWORD  = ""
topic_pub     = "nicolas/proyecto" # Eltopic donde vas a publicar
topic_sub      = 'nicolas/proyecto' # El topic al que te vas a suscribir





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
    # print(f'Datos de la red  (ip/netmask/gw/dns): {mired.ifconfig()}') 
 

    def sub_cb(topic, msg):
        print(f"llego el topic: {topic} con el valor {msg}")


    print("Connecting to MQTT server... ", end="")
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, user=MQTT_USER, password=MQTT_PASSWORD)

    client.set_callback(sub_cb)

    client.connect()

    client.subscribe(topic_sub)

    print(f'Connected to {MQTT_BROKER} MQTT broker, subscribed to {topic_sub} topic')
    print("Connected!")
    prev_weather = ""
    
    def oledMostrar():
        oled.text(f'N monedas = {1}', 2, 40, 1)
        oled.text(f'Total = {1} $', 2, 32, 1)
        oled.show()
        oled.text(f'N monedas = {1}', 2, 40, 0)
        oled.text(f'Total = {1} $', 2, 32, 0)
        
    def notas():
        while True:
            buzzer.duty_u16(32767)
            buzzer.freq(2637)
            time.sleep(0.2)
            buzzer.freq(1568)
            time.sleep(0.2)
    
    
    while True:
        
        distance = sensor.distance_cm()
        print('Distancia:', distance, 'cm')
        
        if distance > 2 and distance < 4:
        

            def sub_cb(topic, msg):
                print(f"llego el topic: {topic} con el valor {msg}")

            def desborde (Timer):   
                global prev_weather
        
                valor = str(random.randint(1,7))
                # valor = '3'
    
                message = valor
                if message != prev_weather:
                    print(f"valor publicado en el topic {topic_pub}: {message}  ")
                    client.publish("nicolas/proyecto", message)
                prev_weather = message


            temporiza.init(period=1000,mode=Timer.PERIODIC,callback=desborde)


            while True:
                print ("esperando") 
                client.wait_msg()
        
        
    