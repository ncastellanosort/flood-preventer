import urequests

uri = 'https://api.openweathermap.org/data/2.5/weather?q=Cordoba,CO&appid=84c3b570d602a28aa69e9796925026a1&units=metric&lang=es'

respuesta = urequests.get(uri)

datos = respuesta.ujson()

print(datos)

respuesta.close()