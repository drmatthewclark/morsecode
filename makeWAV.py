#
# creates WAV files with beeps
#
import wave
import struct
import math

FREQ = 44100
PI = 3.141592653589793
VOL = 32767

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




