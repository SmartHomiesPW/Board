from flask import Flask, render_template
import RPi.GPIO as GPIO
import time as time
import threading

Debounce = 0.1
TRIG = 27
ECHO = 9
state = False

app = Flask(__name__)
@app.route('/')
def Get():
    templateData = {
        'state' : "ON" if state else "OFF"
    }
    return render_template('index.html', **templateData)
@app.route('/c')
def Change():
    global state
    state = not state
    templateData = {
        'state' : "ON" if state else "OFF"
    }
    GPIO.output(TRIG, state)
    return render_template('index.html', **templateData)

def hw():
    global state
    while True:

        if GPIO.input(ECHO):
            start = time.time()
            while GPIO.input(ECHO):
                continue
            end = time.time()
            if end-start < Debounce:
                GPIO.output(TRIG, state)
                state = not state
                print("changed state by detector")
                time.sleep(Debounce)


if __name__ == '__main__':
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TRIG,GPIO.OUT)
    GPIO.setup(ECHO,GPIO.IN)
    GPIO.output(TRIG, state)
    # x = threading.Thread(target=hw, args=())
    # x.start()
    app.run(debug=True, port=5000, host='0.0.0.0')
