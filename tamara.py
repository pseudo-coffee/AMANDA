#!/usr/bin/python

from __future__ import print_function
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from gtts import gTTS

import datetime
import pickle
import os
import time
import pytz
import random
import smtplib
import pyttsx3
import speech_recognition as sr
import wikipedia
import webbrowser
import subprocess
import requests
import json
import random
import string
import playsound

SCOPES = ['https://www.googleapis.com/calendar.readonly']
DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
MONTHS = ["january", "febuary", "march", "april", "may", "june" ,"july" ,"august", "september", "october", "november", "december"]
__OS__ = ['posix', 'nt']


class TextEditorNotFound(Exception):
	"""Return an error if the Text Editor isnt found."""


class Tamara(object):
	global OS
	def __init__(self):
		self.chars = string.ascii_letters + string.digits
		if os.name not in __OS__:
			raise OSError("Your operating system is not compatible with Tamara.")
		else:
			if os.name == __OS__[0]:
				self.OS = 'posix'

			else:
				self.OS = 'nt'		

	def make_filename(self):
		"""
		Generate a string with random characters and use it as
		the filename in speak().
		"""
		length = random.randint(10, 20)
		i = 0
		filename = ''
		while i != length:
			char = ''
			char = random.choice(self.chars)
			filename += char
			i += 1

		return filename

	def speak(self, text):
		"""
		Generate a voice. This will interact with the user.
		"""
		tts = gTTS(text=text, lang='en')
		filename = self.make_filename() + '.mp3'
		tts.save(filename)   # The .mp3 file will be deleted later.
		playsound.playsound(filename)

		if self.OS == 'posix':
			os.system(f"rm -rf {filename}")
		else:
			os.system(f'del /f {filename}')

	@staticmethod
	def take_command():
		"""
		Take voice input from the microphone and convert it into 
		text. 
		"""
		r = sr.Recognizer()  #  it helps to detect audio from the microphone.
		with sr.Microphone() as source:
			print('Listening...')
			r.pause_threshold = 1
			audio = r.listen(source)

		try:
			print('Proccessing...')
			query - r.recognize_google(audio, languages='en-in')
			print(f'User said: {query}')

		except Exception as e:
			print(e)
			print('Could not recognise...')
			return None
		return query

	@staticmethod
	def authenticate_google():
		creds = None
		if os.path.exists('token.pickle'):
			with open('token.pickle', 'rb') as token:
				creds = pickle.load(token)

		# if there are no (valid) credentials available, let the user log in.
		if not creds or not creds.valid:
			if creds and creds.expired and creds.refresh_token():
				creds.refresh(Request())
			else:
				flow = InstalledAppFlow.from_client_secrects_file(
					'credentials.json', SCOPES)
				creds = flow.run_local_server(port=0)

			# save the credentials for the next run
			with open('token.pickle', 'wb') as token:
				pickle.dump(creds, token)

		service = build('calendar', 'v3', credentials=creds)
		return service

	@staticmethod
	def get_events(day, service):
		date = datetime.datetime.combine(day, datetime.datetime.min.time())  # the min time on that day.
		end_date = datetime.datetime.combine(day, datetime.datetime.max.time())  # the max time on that date.
		utc = pytz.UTC
		date = date.astimezone(utc)
		end_date = end_date.astimezone(utc)

		events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(), timeMax=end_date.isoformat(), singleEvents=True, orderBy='startTime').execute()
		events = events_result.get('items', [])

		if not events:
			self.speak('No upcoming events found.')
		else:
			self.speak(f'You have {len(events)} events on this day.')

			for event in events:
				start = event['start'].get('dateTime', event['start'].get('date'))
				print(start, event['summary'])
				start_time = str(start.split('T')[1].split('+')[0].split(':')[0])

				if int(start_time.split(":")[0]) < 12:
					start_time = start_time + "AM"
				else:
					start_time = str(int(start_time.split(":")[0])-12)
					start_time = start_time + "PM"
				self.speak(event['summary'] + 'at' + start_time)

	@staticmethod
	def get_date(text):
		"""
		Get the date from the user.
		"""
		text = text.lower()
		today = datetime.date.today()

		if text.count("today")>0:
			return today

		day = -1
		day_of_week = -1
		month = -1
		year = today.year

		for word in text.split():
			if word in MONTHS:
				month = MONTHS.index(word) + 1

			elif word in DAYS:
				day_of_week = DAYS.index(word)

			elif word.isdigit():
				day = int(word)
			else:
				for ext in DAY_EXTENTIONS:
					found = word.find(ext)
					if found > 0:
						try:
							day = int(word[:found])
						except:
							pass

		if month < today.month and month != -1:
			year = year + 1

		if month == -1 and day != -1:
			if day < today.day:
				month = today.month + 1
			else:
				month = today.month

		if month == -1 and day == -1 and day_of_week == -1:
			current_day_of_week = today.weekday()
			dif = day_of_week - current_day_of_week

			if dif < 0:
				dif += 7
				if text.count("next") >= 1:
					dif += 7
			return today + datetime.date(month=month, day=day, year=year)

	def start_talking(self):
		hour = int(datetime.datetime.now().hour)

		if hour >= 0 and hour < 12:
		    self.speak("Good morning.")
		    print("Good morning.")

		elif hour >= 12 and hour < 18:
		    self.speak("Good afternoon.")
		    print("Good afternoon.")

		else:
		    self.speak("Good evening.")
		    print("Good evening.")

		# TODO: consider adding a welcome tone with the users name.

		# date = datetime.datetime.now().date()
		# time = datetime.datetime.now().strftime("%H:%M:%S")
		# TODO: add a file that will help Tamara know if she's been used before. 
		self.speak(f"My name is Tamara. How may i help you?")
		print("My name is Tamara. How may i help you?")

	def make_notes(self, text):
		date = datetime.datetime.now()
		filename = str(date).replace(":", "-") + "-note.txt"
		with open(filename, 'w') as f:
			f.write(text)

		if self.OS == 'posix':
			if not os.path.isfile('/usr/bin/mousepad'):
				raise TextEditorNotFound("Please install mousepad.")
			else:
				os.system("/user/bin/mousepad")
		else:
			subprocess.Popen(['notepad.exe', filename])


if __name__ == '__main__':
	Tamara().start_talking()
	while True:
		query = Tamara().take_command().lower()

		print(query)
		break

