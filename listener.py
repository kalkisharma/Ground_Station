import pyaudio
import wave
import speech_recognition as sr
from playsound import playsound

import threading
import time

class AudioRecorder():

    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    CHUNK = 1024
    WAVE_OUTPUT_FILENAME = "file.wav"

    def __init__(self):
        self.record = True
        self.audio = pyaudio.PyAudio()
        self.frames = []
        self.stream = []
        self.record_thread = None
        self.listening = False

    def reset(self):
        self.record = True
        self.audio = pyaudio.PyAudio()
        self.frames = []
        self.stream = []
        if self.record_thread!=None:
            self.record_thread.join()

    def start_recording(self, _=None):
        self.reset()
        # Start recording thread
        self.record_thread = threading.Thread(target=self._record)
        self.record_thread.start()

    def _record(self):
        # start Recording
        self.stream = self.audio.open(
                        format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNK
                        )
        #print("RECORDING...")

        while self.record:
            data = self.stream.read(self.CHUNK)
            self.frames.append(data)

        #print("FINISHED RECORDING")

    def stop_recording(self, _=None):
        self.record = False

        # Wait to ensure recording completed
        time.sleep(0.1)
        self.record_thread.join()

        # stop Recording
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

    #def save_recording(self):
        # Save recording
        waveFile = wave.open(self.WAVE_OUTPUT_FILENAME, 'wb')
        waveFile.setnchannels(self.CHANNELS)
        waveFile.setsampwidth(self.audio.get_sample_size(self.FORMAT))
        waveFile.setframerate(self.RATE)
        waveFile.writeframes(b''.join(self.frames))
        waveFile.close()

    def play_recording(self):
        playsound(self.WAVE_OUTPUT_FILENAME)

    def recognize_recording(self):
        r = sr.Recognizer()
        file = sr.AudioFile(self.WAVE_OUTPUT_FILENAME)
        with file as source:
            audio = r.record(source)
        try:
            return(r.recognize_google(audio, show_all=True)['alternative'][0]['transcript'])
        except:
            return('')

if __name__=='__main__':
    ar = AudioRecorder()
    while True:
        ar.start_recording()
        time.sleep(2)
        ar.stop_recording()
        text = ar.recognize_recording()
        if 'hey baby' in text:
            print('Speak Command')
            ar.start_recording()
            ar.listening = True
            time.sleep(5)
            ar.stop_recording()
            text = ar.recognize_recording()
            print(text)
