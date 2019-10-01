import os
from gtts import gTTS
from playsound import playsound

text = 'Saved Packages to Shelf'
language = 'en-us'

obj = gTTS(text=text, lang=language, slow=False)

obj.save('audio_files/save_package.mp3')

playsound('audio_files/save_package.mp3')