"""
import pyaudio
import wave
#import speech_recognition as sr
from playsound import playsound

import threading
import time
import logging

import snowboydecoder
import os

import Shared

class AudioRecorder():

    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    CHUNK = 1024
    WAVE_OUTPUT_FILENAME = "file.wav"

    def __init__(self, modelFile='', sens = 0.5):

        self.detector = snowboydecoder.HotwordDetector(modelFile, sensitivity= sens)


        self.close_thread = False

        self.listen_thread = threading.Thread(target = self.start_listening)


    def reset(self):
        self.record = True
        self.audio = pyaudio.PyAudio()
        self.frames = []
        self.stream = []
        if self.record_thread!=None:
            self.record_thread.join()


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


    def stop_recording(self):
        if self.close_thread:
            print('Stopping audio recorder.', end='', flush=True)

        return self.close_thread

    def detectedCallback(self):
        #print('Recognized keyword. Listening...', end='', flush=True)
        logging.info('Recognized keyword. Listening...')
        Shared.data.audio_lock.acquire()
        Shared.data.listening = True
        Shared.data.audio_command = ('', time.time())
        Shared.data.audio_lock.release()



    def start(self):
        self.close_thread = False
        self.listen_thread.start()

    def start_listening(self):

        self.detector.start(detected_callback=self.detectedCallback,
            interrupt_check=self.stop_recording,
            audio_recorder_callback=self.audioRecorderCallback,
            recording_timeout= 20, # 1 unit of timeout is ~ 220 milliseconds
            sleep_time=0.03)

    def stop(self):
        self.close_thread = True

    def audioRecorderCallback(self, fname):
        print("Converting audio to text")
        
        r = sr.Recognizer()
        with sr.AudioFile(fname) as source:
            audio = r.record(source)  # read the entire audio file
        # recognize speech using Google Speech Recognition

        try:
            val = r.recognize_google(audio, show_all=True)
            os.remove(fname)
            if(len(val)):
                Shared.data.audio_lock.acquire()
                Shared.data.audio_command = (val['alternative'][0]['transcript'],time.time())
                Shared.data.audio_lock.release()

        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
            os.remove(fname)

        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
            os.remove(fname)

        Shared.data.audio_lock.acquire()
        Shared.data.listening = False
        Shared.data.audio_lock.release()
"""
