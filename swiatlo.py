from flask import Flask, render_template
import RPi.GPIO as GPIO
import time
import threading

Debounce = 0.1
TRIG = [12, 20, 21]
ECHO = 9
state = [False] * 3

app = Flask(__name__)

@app.route('/')
def get():
    templateData = {
        'state': "ON" if state else "OFF"
    }
    return render_template('index.html', **templateData)

@app.route('/lights/set/<int:lightId>/<int:newState>')
def change(lightId, newState):
    global state
    # print(newState, type(newState))
    newState = bool(newState)
    if state[lightId] == newState:
        GPIO.output(TRIG[lightId], newState)
        return "light was already " + "ON" if state[lightId] else "OFF", 400
    state[lightId] = newState
    GPIO.output(TRIG[lightId], newState)
    return "changed correctly", 200

# Change by button
def hw():
    global state
    while True:
        if GPIO.input(ECHO):
            start = time.time()
            while GPIO.input(ECHO):
                pass
            end = time.time()
            if end - start < Debounce:
                GPIO.output(TRIG, state)
                state = not state
                time.sleep(Debounce)

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)


    for pin in TRIG:
        GPIO.setup(pin, GPIO.OUT)
        # GPIO.output(pin, state)

    # GPIO.setup(ECHO, GPIO.IN)
    #for i in range(3):
    #    change(i, True)
    #    time.sleep(1)  # Add a delay if needed
    #    change(i, False)
    #    time.sleep(1)

    # Uncomment the following lines if you want to run the button thread
    # x = threading.Thread(target=hw, args=())
    # x.start()

    app.run(debug=True, port=5000, host='0.0.0.0')
