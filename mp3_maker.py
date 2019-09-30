import os
from gtts import gTTS
from playsound import playsound

text = 'Takeoff Completed'
language = 'en-us'

obj = gTTS(text=text, lang=language, slow=False)

obj.save('audio_files/takeoff_end')

playsound('audio_files/takeoff_end')