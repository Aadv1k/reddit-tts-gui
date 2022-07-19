from textwrap import indent
import gtts
import json

tts = gtts.gTTS('There once was a ship that put to sea', lang='en', tld='co.uk')
tts.save('out.mp3')

