import pyaudio
import wave
import speech_recognition as sr
from playsound import playsound

import threading
import time
import logging

class AudioRecorder():

    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    CHUNK = 1024
    WAVE_OUTPUT_FILENAME = "file.wav"

    def __init__(self, _keyword=''):
        self.record = True
        self.audio = pyaudio.PyAudio()
        self.frames = []
        self.stream = []
        self.keyword = _keyword
        self.command = ''
        self.record_thread = None
        self.listening = False
        self.close_thread = False

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

    def keyword_listener(self):
        
        self.listen_thread = threading.Thread(target=self._listen)
        self.listen_thread.start()

    def stop(self):

        self.close_thread = True

    def start(self):

        self.keyword_listener()

    def _listen(self, loop_time=3, listen_time=5):
        #ar = AudioRecorder()
        logging.info("RUNNING LISTENING THREAD")
        while not self.close_thread:
            self.start_recording()
            time.sleep(loop_time)
            self.stop_recording()
            text = self.recognize_recording()
            if text!='':
                print(text)
            if self.keyword in text:
                print('SPEAK COMMAND')
                self.start_recording()
                self.listening = True
                time.sleep(listen_time)
                self.stop_recording()
                text = self.recognize_recording()
                print(f'COMMAND: {text}')
                self.command = text
                self.listening = False
        return
