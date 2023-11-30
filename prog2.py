

#########
from flask import Flask, render_template
import RPi.GPIO as GPIO
import time
import threading

class keypad():
    # CONSTANTS
    KEYPAD = [
        [1,   2,   3, "A"],
        [4,   5,   6, "B"],
        [7,   8,   9, "C"],
        ["*", 0, "#", "D"]
    ]

    #COLUMN      = [25, 24, 23, 18]
    #ROW         = [22, 21, 17, 4]
    COLUMN      = [22, 27, 17]
    ROW         = [24, 23, 10]
    def __init__(self):
        GPIO.setmode(GPIO.BCM)

    def getKey(self):
        # Set all columns as output low
        for row in self.ROW:
            GPIO.setup(row, GPIO.OUT)
            GPIO.output(row, GPIO.LOW)

        for col in self.COLUMN:
            GPIO.setup(col, GPIO.OUT)
            GPIO.output(col, GPIO.LOW)

        # Set all rows as input
        for row in self.ROW:
            GPIO.setup(row, GPIO.IN, pull_up_down = GPIO.PUD_UP)

        for col in self.COLUMN:
            GPIO.output(col, GPIO.HIGH)
            for row in self.ROW:
                if GPIO.input(row) == 1:
                    return self.KEYPAD[self.ROW.index(row)][self.COLUMN.index(col)]
            GPIO.output(col, GPIO.LOW)
        return
        # Scan rows for pushed key/button
        # A valid key press should set "rowVal"  between 0 and 3.
        rowVal = -1
        for i in range(len(self.ROW)):
            tmpRead = GPIO.input(self.ROW[i])
            if tmpRead == 0:
                rowVal = i

        # if rowVal is not 0 thru 3 then no button was pressed and we can exit
        if rowVal <0 or rowVal >3:
            self.exit()
            return

        # Convert columns to input
        for j in range(len(self.COLUMN)):
                GPIO.setup(self.COLUMN[j], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # Switch the i-th row found from scan to output
        GPIO.setup(self.ROW[rowVal], GPIO.OUT)
        GPIO.output(self.ROW[rowVal], GPIO.HIGH)

        # Scan columns for still-pushed key/button
        # A valid key press should set "colVal"  between 0 and 3.
        colVal = -1
        for j in range(len(self.COLUMN)):
            tmpRead = GPIO.input(self.COLUMN[j])
            if tmpRead == 1:
                colVal=j

        # if colVal is not 0 thru 3 then no button was pressed and we can exit
        if colVal < 0 or colVal > 3:
            self.exit()
            return

        # Return the value of the key pressed
        self.exit()
        return self.KEYPAD[rowVal][colVal]

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


    ##test klawiatura
    kp = keypad()

    while 1:
        digit = None
        while digit == None:
            digit = kp.getKey()
            sleep(1)
        print(digit)


    #test czujnik ruchu
    #GPIO.setup(12,GPIO.IN)
    #while 1:
    #    GPIO.output(21,GPIO.input(12))
    #    time.sleep(0.1)



   ## for pin in TRIG:
     ##   GPIO.setup(pin, GPIO.OUT)
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

   # app.run(debug=True, port=5000, host='0.0.0.0')
