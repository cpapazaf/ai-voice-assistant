# Import the required module for text 
# to speech conversion
from gtts import gTTS
from io import BytesIO
from pyaudio import PyAudio, paInt16
import pygame

# This module is imported so that we can 
# play the converted audio
import os

# The text that you want to convert to audio
mytext = 'Welcome to geeksforgeeks Joe!'

# Passing the text and language to the engine, 
# here we have marked slow=False. Which tells 
# the module that the converted audio should 
# have a high speed
tts = gTTS(text=mytext, lang='en', slow=False)

fp = BytesIO()
tts.write_to_fp(fp)
fp.seek(0)

print('fp')

pygame.init()
pygame.mixer.init()
pygame.mixer.music.load(fp)
pygame.mixer.music.play()
while pygame.mixer.music.get_busy():
    pygame.time.Clock().tick(10)