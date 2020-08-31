#!/usr/bin/python

import sys
from random import gauss
import wave
import struct
import math
import os
# global setup stuff

global wavefile
wavefile = None

# set speed
wordsPerMinute = 20


dotLength = 60.0/(wordsPerMinute * 41) # based on PARIS

dashLength = 3 * dotLength
pauseLength = dotLength           # used for pauses in letters for old telegraph codes, 1+1 = 2
letterPauseLength = dotLength * 3 # pause between letters is 3 dots, but since
                                  # each letter has a dot pause, this is added to make 3 dots pause.

wordPauseLength = dotLength * 5   # pause between words, 5 + 1 letter pause for total of 6
morseLLength = dashLength * 2     # special long dash for old Morse L
morse0Length = dashLength * 3     # special long dash for old Morse 0
randomAmount = 0.07  # 7% variation in length, gaussian randomness
gpioPin = 26

# words per minute is computed using the word PARIS, so this
# figure below is worked out using standard characters and spacings
# PARIS has 50 elements
#
print( 'telegraph rate is {0:.3f}'.format(wordsPerMinute), " words per minute")


FREQ = 2000  # hi freq not required for this application
PI = 3.141592653589793
VOL = 32767

# standard messages
endOfMessage = 'www.-.-.'  
endOfTransmission = '.-.-.w'
endOfWork = '...-.-'

# make it a little less mechanically uniform with a Gaussian
# deviation of 5%
randomDeviation = dotLength * randomAmount

On = True
Off = False

def makebeep(freq, length, vol, wavfile):

    samples = int(FREQ * length)
    coef = PI*freq/FREQ
    for i in range(0, samples):
        value = int(math.sin(i*coef)*vol)
        packed_value = struct.pack('h', value)
        wavfile.writeframes(packed_value)

def openfile(fname):
    noise_output = wave.open(fname, 'wb')
    noise_output.setparams((1, 2, FREQ, 1, 'NONE', 'not compressed'))
    return noise_output



#
# table to define dots and dashes 
# this table is 1920 telegraph code used in mechanical telegraph
# sounders, not modern international morse code.
# https://en.wikipedia.org/wiki/Telegraph_code#Comparison_of_codes
#
# this variation has pauses within the letters
#
def morse1920(x):
    return {
        ' ': 'w',   # word pause
        'A': '.-',
        'B': '-...',
        'C': '..d.',
        'D': '-..',
        'E': '.',
        'F': '.-.',
        'G': '--.',
        'H': '....',
        'I': '..',
        'J': '-.-.',
        'K': '-.-',
        'L': 'L',
        'M': '--',
        'N': '-.',
        'O': '.d.',
        'P': '.....',
        'Q': '..-.',
        'R': '.d..',
        'S': '...',
        'T': '-',
        'U': '..-',
        'V': '...-',
        'W': '.--',
        'X': '.-..',
        'Y': '..d..',
        'Z': '...d.',
        '&': '.d...',
        '1': '.--.',
        '2': '..-..',
        '3': '...-',
        '4': '....-',
        '5': '---',
        '6': '......',
        '7': '--..',
        '8': '-....',
        '9': '-..-.',
        '0': 'z',
        '.': '..--..',
        ':': '-.-d..',
        ';': '.-.-.',
        ',': '.-.-',
        '?': '-..-.',
        '!': '---.',
        '\n' : 'w----',
        '('  : '.-..-',
        ')'  : '.-..-',
        }.get(x, ' ')  # default is space

#
# table to define dots and dashes 
# this is the modern international morse code from 1851
# 
# ITU recommendation ITU-R M.1677.1 (10/2009)
# http://www.itu.int/dms_pubrec/itu-r/rec/m/R-REC-M.1677-1-200910-I!!PDF-E.pdf
# oddly, the IMC has no ampersand
#
def morseIMC(x):
    return {
        ' ': 'w',   # word pause
        'A': '.-',
        'B': '-...',
        'C': '-.-.',
        'D': '-..',
        'E': '.',
        'F': '..-.',
        'G': '--.',
        'H': '....',
        'I': '..',
        'J': '.---',
        'K': '-.-',
        'L': '.-..',
        'M': '--',
        'N': '-.',
        'O': '---',
        'P': '.--.',
        'Q': '--.-',
        'R': '.-.',
        'S': '...',
        'T': '-',
        'U': '..-',
        'V': '...-',
        'W': '.--',
        'X': '-..-',
        'Y': '-.--',
        'Z': '--..',
        '1': '.----',
        '2': '..---',
        '3': '...--',
        '4': '....-',
        '5': '.....',
        '6': '-....',
        '7': '--...',
        '8': '---..',
        '9': '----.',
        '0': '-----',
        '.': '.-.-.-',
        ',': '--..--',
        ':': '---...',
        '?': '..--..',
        '\'': '.----.',
        '-': '-....-',
        '/': '-..-.',
        '(': '-.--.',
        ')': '-.--.-',
        '"': '.-..-.',
        '=': '-...-',
        '+': '.-.-.',
        '@': '.--.-.',
        '%': '-----l-..-.l-----',  # 0/0 
        #unichr(247): '---...',  # division
        #unichr(2715) : '-..-',  # multiplication
        #unichr(2032) : '.----.',  # multiplication
        #unichr(2032) : '.----.',  # minute symbol
        #unichr(2033) : '.----.l.----.',  # second symbol
        }.get(x, ' ')  # default is space

#
# defines which morse code variation to use
#
def morse(char):
        return morseIMC(char)

# wrapper for pulses
def pulse(duration):
        freq = 1000
        vol = 32767
        duration += gauss(0, randomDeviation)
        makebeep(freq, duration, vol, wavefile)
        makebeep(freq, dotLength, 0, wavefile)
        return duration + dotLength

def wait(duration):
        freq = 1000
        vol = 32767
        makebeep(freq, dotLength, 0, wavefile)  
        return dotLength
        

def dot():
        print("dit ")
        return pulse(dotLength)

def dash():
        print("dah ")
        return pulse(dashLength)

def morseL():    # special for old morse L
        print("dahh ")
        return pulse(morseLLength)

def morse0():   # special dash for old morse 0
        print("dahhh ")
        return pulse(morse0Length)

def midLetterPause():   # special mid-character pause for old morse
        print("pause ",)
        return wait(pauseLength)

def letterPause():  # pause between letters
        print("\t\t-letter")
        return wait(letterPauseLength)

def wordPause():  # pause between words
        print("*-word space-*")
        return wait(wordPauseLength)


def space():
        print("space")
        return wait(wordPauseLength)


def sendCode(code):
        t = 0
        for dahdit in code:
                if dahdit == '.':
                        t += dot()
                elif dahdit == '-':
                        t += dash()
                elif dahdit == 'd':
                        t += midLetterPause()  # for old Vail US telegraphy
                elif dahdit == 'w':
                        t += wordPause()  # pause between words
                elif dahdit == 'z':
                        t += morse0()     # very long dash
                elif dahdit == 'L':
                        t += morseL()     # long dash
                elif dahdit == 'l':
                        t += letterPause() # pause between letters
                else:  # any other character, or an actual space
                        print("unexpected letter: ", dahdit)
                        t += space()
        t += letterPause()
        return t

# clean up
def cleanup():
    global wavefile
    wavefile.close()

# setup IO ports
def setup():
    global wavefile
    wavefile = openfile('morse.wav')


def main():
# read input and send the code
#
   
    data = sys.argv[1:]
    setup()
    t = 0.0
    chars = 0
    for x in range(0, len(data)):
        dline = data[x].upper().rstrip()
        for char in dline:      
            print (char," ",)
            morseCode = morse(char)
            t += sendCode(morseCode)
            chars += 1

    cleanup()
    words = chars/5.0
    print("%i chars %f seconds %f wpm" % (chars, t, words*60/t))
    os.system("mplayer morse.wav")
#
# realistic end of message codes
#
#sendCode(endOfMessage)
#sendCode(endOfTransmission)
#sendCode(endOfWork)

main()
