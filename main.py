import network
import socket
from machine import Pin, PWM
import utime

# WiFi Credentials
SSID = "Galaxy A16"
PASSWORD = "yipb85501"

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

while not wlan.isconnected():
    print("Connecting to WiFi...")
    utime.sleep(1)

print("Connected:", wlan.ifconfig())

# Onboard LED
led = Pin(25, Pin.OUT)

# Drive Motor (Forward/Backward)
drive1 = Pin(16, Pin.OUT)
drive2 = Pin(17, Pin.OUT)
pwm_drive = PWM(Pin(18))
pwm_drive.freq(1000)

# Steering Motor (Left/Right)
steer1 = Pin(19, Pin.OUT)
steer2 = Pin(26, Pin.OUT)
pwm_steer = PWM(Pin(15))
pwm_steer.freq(1000)

# Set speed
def set_speed(speed=90000):
    pwm_drive.duty_u16(speed)
    pwm_steer.duty_u16(speed)

# Movement functions
def backward():
    set_speed()
    drive1.value(1)
    drive2.value(0)
    led.value(1)
    return "Moving Forward"

def forward():
    set_speed()
    drive1.value(0)
    drive2.value(1)
    led.value(1)
    return "Moving Backward"

def stop_drive():
    drive1.value(0)
    drive2.value(0)
    led.value(0)
    return "Drive Stopped"

def turn_left():
    set_speed()
    steer1.value(1)
    steer2.value(0)
    led.value(1)
    return "Turning Left"

def turn_right():
    set_speed()
    steer1.value(0)
    steer2.value(1)
    led.value(1)
    return "Turning Right"

def stop_steering():
    steer1.value(0)
    steer2.value(0)
    led.value(0)
    return "Steering Stopped"

# HTML Web Page
html = """<!DOCTYPE html>
<html>
<head>
    <title>Pico Car Control</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            background-color: #f4f4f4;
            padding: 20px;
        }
        h2 {
            color: #333;
        }
        .container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        .button {
            background-color: #007BFF;
            border: none;
            color: white;
            padding: 15px 30px;
            margin: 10px;
            font-size: 18px;
            cursor: pointer;
            border-radius: 5px;
            transition: background 0.3s, transform 0.2s;
        }
        .button:hover {
            background-color: #0056b3;
            transform: scale(1.1);
        }
        .button:active {
            background-color: #00408a;
            transform: scale(0.95);
        }
        .controls {
            display: grid;
            grid-template-columns: repeat(3, auto);
            gap: 10px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <h2>Car Control</h2>
    <div class="container">
        <div class="controls">
            <button class="button" onclick="sendRequest('/left')">⬅ Left</button>
            <button class="button" onclick="sendRequest('/forward')">⬆ Forward</button>
            <button class="button" onclick="sendRequest('/right')">➡ Right</button>
            <button class="button" onclick="sendRequest('/stop_steering')">⏹ Stop Steering</button>
            <button class="button" onclick="sendRequest('/backward')">⬇ Backward</button>
            <button class="button" onclick="sendRequest('/stop_drive')">⏹ Stop</button>
        </div>
    </div>
    <script>
        function sendRequest(path) {
            var xhr = new XMLHttpRequest();
            xhr.open("GET", path, true);
            xhr.send();
        }
    </script>
</body>
</html>

"""

# Web Server
def web_server():
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(5)
    print("Listening on", addr)

    while True:
        cl, addr = s.accept()
        print("Client connected from", addr)
        request = cl.recv(1024).decode()
        print("Request:", request)

        response = ""
        if "/forward" in request:
            response = forward()
        elif "/backward" in request:
            response = backward()
        elif "/stop_drive" in request:
            response = stop_drive()
        elif "/left" in request:
            response = turn_left()
        elif "/right" in request:
            response = turn_right()
        elif "/stop_steering" in request:
            response = stop_steering()

        cl.send("HTTP/1.1 200 OK\nContent-Type: text/html\n\n")
        cl.send(html)
        cl.close()

web_server()
