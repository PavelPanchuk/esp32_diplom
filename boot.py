
from machine import UART, Pin, SoftI2C, RTC
import am2320
import _thread
import time
import time
import socket
import machine
import network


#настройка сети
sta = network.WLAN(network.STA_IF)
if not sta.isconnected():
    print('connecting to network...')
    sta.active(True)
    #sta.connect('your wifi ssid', 'your wifi password')
    sta.connect('Rostelecom-29', 'doc1213DOC-')
    while not sta.isconnected():
        pass
print('network config:', sta.ifconfig())

# ************************
# Configure the socket connection
# over TCP/IP


# AF_INET - use Internet Protocol v4 addresses
# SOCK_STREAM means that it is a TCP socket.
# SOCK_DGRAM means that it is a UDP socket.
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('',80)) # specifies that the socket is reachable 
#                 by any address the machine happens to have
s.listen(5)     # max of 5 socket connections





red=[]
blue = []
red_down = []
blue_down = []

status = []
co2 = 0

rtc = RTC()
i2c = SoftI2C(freq=100000, scl=Pin(9), sda=Pin(8))
sensor = am2320.AM2320(i2c)
time.sleep_ms(1000)

def co2_pwm():
  co2pin = Pin(10, Pin.IN)
  while (co2pin.value()!=0):
    co2pin.value()
  while (co2pin.value()==0):
    co2pin.value()
  start=time.ticks_us()
  while (co2pin.value()==1):
    co2pin.value()
  stop=time.ticks_us()
  ms=int((stop-start)/1000)
  ppm=5000*(ms-2)/1000
  return ppm #int((stop-start)/1000)
  

def as_read(tx_pin, rx_pin):
  red = []
  uart = UART(1, baudrate=115200, tx=tx_pin, rx=rx_pin)
  uart.write('ATCDATA\r\n')
  time.sleep_ms(50)
  data=uart.readline()
  uart.deinit()
  data=str(data)
  data=data.replace("b'"," ")
  data=data.replace("OK\\n'","")
  data=data.replace(",","")
  return data

# rtc.datetime((2022, 6, 2, 4, 22, 32, 36, 0))

def measure_test():
  sensor.measure()
  D = str(rtc.datetime())
  D = D.replace("(","")
  D = D.replace(")","")
  D = D.replace(",","")
  D = D + " "
  T = str(sensor.temperature()) + " "
  H = str(sensor.humidity()) + " "
  blue = as_read(7,6)
  red = as_read(5,4)
  blue_down = as_read(2,3)
  red_down = as_read(0,1)
  return D, T, H, blue, red, blue_down, red_down
  

  
def measure_task():
  while(1):
    sensor.measure()
    D = str(rtc.datetime())
    D = D.replace("(","")
    D = D.replace(")","")
    D = D.replace(",","")
    D = D + " "
    T = str(sensor.temperature()) + " "
    H = str(sensor.humidity()) + " "
    C = str(co2_pwm()) + " "

    blue = as_read(7,6)
    red = as_read(5,4)
    blue_down = as_read(2,3)
    red_down = as_read(0,1)

    data = open("data.txt", "a")
    #data.write(str(time.ticks_ms())+"\n")
    #data.write(str(rtc.datetime())+" ")
    #data.write("T= "+str(sensor.temperature())+" "+"H= "+str(sensor.humidity())+" ") #+"\n")
    #data.write("CO2= " + str(co2_pwm())+" ")
    #data.write(blue_read()+red_read())
    #data.write(blue_down_read() + red_down_read())
    data.write(D + T + H + C + blue + red + blue_down + red_down + '\n')
    data.close()
    
    print("T=",sensor.temperature(),"C ", "H=", sensor.humidity(), "% ","CO2=",co2_pwm(),"ppm")
    print(blue, red)
    print(blue_down, red_down)
    print("\r\n");
    
    time.sleep_ms(600*1000)

    
def web_server():
#настройка сети
  def web_page():
      
      html_page = """    
      <html>    
      <head>    
      <meta content="width=device-width, initial-scale=1" name="viewport">
       
    <meta charset="UTF-8">
    <title>Нир</title>
 
  </meta>    
      </head>    
      <body>    
      <center><h2>Датчик температуры, освещённости, уровень СО2</h2></center>    
  <div class="window">
      <h3>Температура</h3>
      <p id="Температура">""" + str(sensor.temperature()) + """С°</p>
    </div>
    <div class="window">
      <h3>Уровень CO2</h3>
      <p id="co2">""" + str(co2_pwm()) + """ppm</p>
    </div>
    <div class="window">
      <h3>Уровень света</h3>
      <p id="light">""" + "light_state" + """</p>
    </div>
    <div class="window">
      <h3>Уровень влажности</h3>
      <p id="light">""" + str(sensor.humidity())+ """%</p>
    </div>
      </body>    
      </html>"""  
      return html_page   
  sensor.measure()
  D = str(rtc.datetime())
  D = D.replace("(","")
  D = D.replace(")","")
  D = D.replace(",","")
  D = D + " "
  T = str(sensor.temperature()) + " "
  H = str(sensor.humidity()) + " "
  C = str(co2_pwm()) + " "
  blue = as_read(7,6)
  red = as_read(5,4)
  blue_down = as_read(2,3)
  red_down = as_read(0,1)

  data = open("data.txt", "a")
    #data.write(str(time.ticks_ms())+"\n")
    #data.write(str(rtc.datetime())+" ")
    #data.write("T= "+str(sensor.temperature())+" "+"H= "+str(sensor.humidity())+" ") #+"\n")
    #data.write("CO2= " + str(co2_pwm())+" ")
    #data.write(blue_read()+red_read())
    #data.write(blue_down_read() + red_down_read())
  data.write(D + T + H + C + blue + red + blue_down + red_down + '\n')
  data.close()
    
  print("T=",sensor.temperature(),"C ", "H=", sensor.humidity(), "% ","CO2=",co2_pwm(),"ppm")
  print(blue, red)
  print(blue_down, red_down)
  print("\r\n");
  while True:
  
      # Socket accept() 
      conn, addr = s.accept()
      print("Got connection from %s" % str(addr))
      
      # Socket receive()
      request=conn.recv(1024)
      print("")
      print("")
      print("Content %s" % str(request))

      # Socket send()
      request = str(request)
      led_on = request.find('/?LED=1')
      led_off = request.find('/?LED=0')
      led_blink = request.find('/?LED=2')
      if led_on == 6:
          print('LED ON')
          print(str(led_on))
          led.value(1)
          if isLedBlinking==True:
              tim0.deinit()
              isLedBlinking = False
          
      elif led_off == 6:
          print('LED OFF')
          print(str(led_off))
          led.value(0)
          if isLedBlinking==True:
              tim0.deinit()
              isLedBlinking = False
          
      elif led_blink == 6:
          print('LED Blinking')
          print(str(led_blink))
          isLedBlinking = True
          tim0.init(period=500, mode=machine.Timer.PERIODIC, callback=handle_callback)
          
      response = web_page()
      conn.send('HTTP/1.1 200 OK\n')
      conn.send('Content-Type: text/html\n')
      conn.send('Connection: close\n\n')
      conn.sendall(response)
      
      # Socket close()
      conn.close()


while(1):
    web_server()
#_thread.start_new_thread(web_server,())

#_thread.start_new_thread(measure_task,())



def read_all_data():
  data=open("data.txt","r")
  for line in data:
    print(line)
  data.close()


