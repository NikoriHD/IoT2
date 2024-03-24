import network
import espnow
import socket
import time
import machine
import neopixel

def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print('Connecting to Wi-Fi...')
        wlan.connect(ssid, password)

        while not wlan.isconnected():
            pass

    print('Wi-Fi connected!')
    print('IP address:', wlan.ifconfig()[0])

wifi_ssid = "OnePlusN"
wifi_password = "Yeet1234"
connect_to_wifi(wifi_ssid, wifi_password)

esp_now = espnow.ESPNow()
esp_now.active(True)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    server_socket.bind(('0.0.0.0', 1234))
except OSError as e:
    if e.args[0] == 98:
        print("Address already in use. Closing the socket.")
        server_socket.close()
        time.sleep(1)
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('0.0.0.0', 1234))

server_socket.listen(1)

print('Waiting for client connection...')

client_socket, client_address = server_socket.accept()
print('Client connected:', client_address)

BUZZER_PIN = 26
buzzer_PWM_object = machine.PWM(machine.Pin(BUZZER_PIN), freq=440, duty=0)

n = 12
p = 25
np = neopixel.NeoPixel(machine.Pin(p), n)

def play_buzzer(duration, frequency=440, duty=512):
    buzzer_PWM_object.freq(frequency)
    buzzer_PWM_object.duty(duty)
    time.sleep_ms(duration)
    buzzer_PWM_object.duty(0)
    time.sleep(0.1)

hello_msg = b'Hello, world!'
client_socket.sendall(hello_msg)

station = network.WLAN(network.STA_IF)
station.active(True)
esp_now = espnow.ESPNow()
esp_now.active(True)

while True:
    host, msg = esp_now.recv()
    if msg:
        print('Received from ESP-NOW:', msg)
        if msg == b'end':
            break

        if b'Sensor 2 - Digital v\xc3\xa6rdi: 1' in msg:
            print("Triggering buzzer...")
            play_buzzer(1000, frequency=440, duty=512)

        if b'Luftfugtighed:' in msg:
            luftfugtighed_value = int(msg.split(b'Luftfugtighed: ')[1].split(b'|')[0])

            for i in range(12):
                threshold = 5 * (i + 1)
                if luftfugtighed_value < threshold:
                    np[i] = (50, 50, 50)
                else:
                    np[i] = (0, 0, 0)
            np.write()

        print('Sending to client:', msg)
        client_socket.sendall(msg)

client_socket.close()
server_socket.close()
print('Connection closed')
print('Connection closed at the host.')
