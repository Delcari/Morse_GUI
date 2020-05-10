import RPi.GPIO as GPIO
import _thread
import queue
import string 
import time

import kivy

kivy.require('1.11.0')

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

from kivy.uix.widget import Widget


GPIO.setmode(GPIO.BOARD)

#Setup GPIO pins
GPIO.setup(7, GPIO.OUT)
GPIO.output(7, 0)

from kivy.config import Config

#Set window dimensions
Config.set('graphics', 'width', '200')
Config.set('graphics', 'height', '150')

#Creates a Queue
q = queue.Queue()

#converts index of letters to morse_code
def toMorseCode(indexList):
    #Array of letters of the alphabet in morse code
    MorseCode = [".-", "-...", "-.-.", "-..", ".", "..-.",
                "--.", "....", "..", ".---", "-.-", ".-..",
                "--", "-.", "---", ".--.", "--.-", ".-.", 
                "...", "-", "..-", "...-", ".--", "-..-",
                "-.--", "--.."]
    result = ""
    for index in indexList:
        result += MorseCode[int(index)]

    return result

#converts letters to their respective index (ie. 2 = c)
def toIndicies(input):
    myList = []
    for char in input:
        myList.append(str(string.ascii_lowercase.index(char)))
    return myList

#blink LED
def Blink(sleep, MorseCode):
    GPIO.output(7, GPIO.HIGH)
    time.sleep(sleep)
    GPIO.output(7, GPIO.LOW)
    time.sleep(0.5)

#blink short/long
def MorseCode(MorseCode):
    for item in MorseCode:
        if (item == "-"):
            Blink(0.75, MorseCode) 
        else:
            Blink(0.25, MorseCode)

#function which completes the tasks in the queue
def runQueue():
    while True:
        #gets the item at the end of the queue
        #first in first out
        item = q.get()
        print('Running task', item)
        MorseCode(item)
        q.task_done()
        print('Task compeleted')


class Controller(GridLayout):
    #Triggered off button pressed (SUBMIT)
    def button_pressed(self, instance):
        #Makes the textBox text lowercase
        thisInput = self.textBox.text.lower()

        #-----------------------------Debugging-----------------------------
        #print("Index List: " + str(self.toIndicies(thisInput)))
        #print("Morse Code: " + self.toMorseCode(self.toIndicies(thisInput))
        #-------------------------------------------------------------------

        #conversions
        textMorseCode = toMorseCode(toIndicies(thisInput))
        #Adds the text to the queue
        q.put(textMorseCode)



    def __init__(self, **kwargs):
        super(Controller, self).__init__(**kwargs)

        self.cols = 1

        #Heading
        self.heading = Label()
        self.heading.font_size = 30
        self.heading.text = "Morse Code"
        self.heading.bold = True

        self.add_widget(self.heading)

        #Textbox
        self.textBox = TextInput()
        self.textBox.font_size = 25


        #filters out chars that aren't alphabetic and only allows 12 characters
        #to be inserted into the textbox
        def filterNonAlphaChars(text, fromUndo=True):
            #length of the text in the textbox is 12
            if (len(self.textBox.text) == 12):
                return ""
            #the input text exists in the alphabet 
            elif(text.isalpha()):
                return text
                
        #Restricts the text input 
        #to length of 12
        #& prevents numeric/symbol input
        self.textBox.input_filter = filterNonAlphaChars

        self.textBox.multiline = False
        self.add_widget(self.textBox)
        
        #submit button
        submitButton = Button()
        submitButton.bind(on_press=self.button_pressed)
        submitButton.text = "SUBMIT"
        submitButton.font_size = 15
        submitButton.bold = True
        self.add_widget(submitButton)
    



class MyApp(App):
    def build(self):
        self.title = '4.3D'
        return Controller()

#Runs the MorseCode function on the Queued list of text
_thread.start_new_thread(runQueue, ())
MyApp().run()
GPIO.cleanup()
