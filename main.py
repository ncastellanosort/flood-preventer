from hcsr04 import HCSR04
from ssd1306 import SSD1306_I2C
from machine import Pin as pin, PWM, I2C, Timer
import network, time, random, urequests
import ufirebase as firebase


temporiza = Timer(0)                    
prev_weather = 0

i2c = I2C(0,sda=pin(2),scl=pin(5),freq=40000)
oled = SSD1306_I2C(128,64,i2c)
sensor = HCSR04(trigger_pin=18, echo_pin=19, echo_timeout_us=5000)
buzzer = PWM(pin(15))
buzzer.duty_u16(0)


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
    
    
    firebase.setURL("https://inundaciones-b944d-default-rtdb.firebaseio.com/")
    
   
    uriWeather = 'https://api.openweathermap.org/data/2.5/weather?q=Cordoba,CO&appid=84c3b570d602a28aa69e9796925026a1&units=metric&lang=es'

    respuesta = urequests.get(uriWeather)

    datos = respuesta.json()
    
    hay_nubes = datos['weather'][0]['main']
    descripcionNubes = datos['weather'][0]['description']
    nubosidad = datos['clouds']['all']
    velocidadViento = datos['wind']['speed']
    humedadClima = datos['main']['humidity']
    
    
    print(f'\nEstado del clima: {hay_nubes}')
    print(f'Descripcion del clima: {descripcionNubes}')
    print(f'Nubosidad: {nubosidad} %')
    print(f'Velocidad del viento: {velocidadViento} km/h')
    print(f'Humedad: {humedadClima} %\n')

    respuesta.close()
    # hasta aca


    def alarmaYmqttmssgs():

        x = 0 
        while x < 15:
            buzzer.duty_u16(32767)

            firebase.put("Inundaciones/alertas", "ALERTA DE INUNDACION", bg=0)
            firebase.delete("Inundaciones/alertas")
            
            randomX1 = random.randint(3,110)
            randomX2 = random.randint(3,110)
            randomX3 = random.randint(3,110)
            
            
            randomY1 = random.randint(3,56)
            randomY2 = random.randint(3,56)
            randomY3 = random.randint(3,56)
            
            time.sleep(0.1)
            buzzer.freq(2637)
            time.sleep(0.1)
            oled.text(f'ALERTA', randomX1, randomY1, 1)
            oled.show()
            oled.text(f'ALERTA', randomX1, randomY1, 0)
            buzzer.freq(1568)
            
            time.sleep(0.1)
            buzzer.freq(2637)
            time.sleep(0.1)
            oled.text(f'ALERTA', randomX2, randomY2, 1)
            oled.show()
            oled.text(f'ALERTA', randomX2, randomY2, 0)
            buzzer.freq(1568)
            
            time.sleep(0.1)
            buzzer.freq(2637)
            time.sleep(0.1)
            oled.text(f'ALERTA', randomX3, randomY3, 1)
            oled.show()
            oled.text(f'ALERTA', randomX3, randomY3, 0)
            buzzer.freq(1568)
            
            x += 1
            
        buzzer.duty_u16(0)
        oled.poweroff()
    
    
    while True:
        
        distance = round(sensor.distance_cm(), 1)

        firebase.put("Inundaciones/sensor/distancia", str(distance) + 'cm', bg=0)
        
        firebase.put("Inundaciones/clima/estado_clima", str(hay_nubes), bg=0)
        firebase.put("Inundaciones/clima/descripcion_clima", str(descripcionNubes), bg=0)
        firebase.put("Inundaciones/clima/nubosidad", str(nubosidad) + '%', bg=0)
        firebase.put("Inundaciones/clima/velocidad_viento", str(velocidadViento) + 'km/h', bg=0)
        firebase.put("Inundaciones/clima/humedad", str(humedadClima) + '%', bg=0)
        
        if distance > 9:
            firebase.put("Inundaciones/nivel_agua/estado", "Sin preocupacion", bg=0)
            oled.text(f'Alerta a 3m', 17, 28, 1)
            oled.text(f'Distancia agua:', 2, 42, 1)
            oled.text(f'{distance} m', 2, 52, 1)
            oled.show()
            oled.text(f'Distancia agua:', 2, 42, 0)
            oled.text(f'{distance} m', 2, 52, 0)
            oled.text(f'Alerta a 3m', 17, 28, 0)
        
        elif distance > 6.3 and distance < 8.1:
            firebase.put("Inundaciones/nivel_agua/estado", "Normal", bg=0)
            oled.text(f'-NIVEL DE AGUA-', 2, 28, 1)
            oled.text(f'Normal', 17, 42, 1)
            oled.show()
            oled.text(f'Normal', 17, 42, 0)
            oled.text(f'-NIVEL DE AGUA-', 2, 28, 0)
        
        elif distance > 4.1 and distance < 6.2 and nubosidad > 55:
            firebase.put("Inundaciones/nivel_agua/estado", "Nivel de agua Creciente", bg=0)
            oled.text(f'-NIVEL DE AGUA-', 2, 28, 1)
            oled.text(f'Creciente', 17, 42, 1)
            oled.show()
            oled.text(f'Creciente', 17, 42, 0)
            oled.text(f'-NIVEL DE AGUA-', 2, 28, 0)
            
            
        elif distance > 3.5 and distance < 4 and nubosidad > 65 and velocidadViento > 0.5 and velocidadViento < 0.9:
            firebase.put("Inundaciones/nivel_agua/estado", "Peligro, este atento a los niveles del sensor", bg=0)
            oled.text(f'-NIVEL DE AGUA-', 2, 28, 1)
            oled.text(f'Peligro', 17, 42, 1)
            oled.show()
            oled.text(f'Peligro', 17, 42, 0)
            oled.text(f'-NIVEL DE AGUA-', 2, 28, 0)

        
        elif distance > 0 and distance < 3.1 and nubosidad > 75 and velocidadViento > 1:
            alarmaYmqttmssgs()
            firebase.put("Inundaciones/estado", "Peligro Extremo, evacue la zona" + '%', bg=0)
            

        
        
    