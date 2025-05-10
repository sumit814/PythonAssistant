import speech_recognition as sr
import webbrowser
import pyttsx3
import musicLibrary
import requests
from openai import OpenAI
from gtts import gTTS
import pygame
import os
from datetime import datetime

# API Keys
newsapi = "<your api key>"
weather_api_key = "<your api key>"

# Initialize
recognizer = sr.Recognizer()
engine = pyttsx3.init() 

# Voice Speak
def speak(text):
    tts = gTTS(text)
    tts.save('temp.mp3') 
    pygame.mixer.init()
    pygame.mixer.music.load('temp.mp3')
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.music.unload()
    os.remove("temp.mp3") 

# OpenAI Integration
def aiProcess(command):
    client = OpenAI(api_key="<your api key>")  # Add your OpenAI key here
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a virtual assistant named Alexa skilled in general tasks like Alexa and Google Cloud. Give short responses please"},
            {"role": "user", "content": command}
        ]
    )
    return completion.choices[0].message.content

# Note Writing
def write_note(text):
    with open("notes.txt", "a") as file:
        file.write(text + "\n")
    speak("Note saved successfully")

def read_notes():
    try:
        with open("notes.txt", "r") as file:
            notes = file.read()
            speak("Here are your notes:")
            speak(notes)
    except:
        speak("No notes found.")

# Weather Function
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}&units=metric"
    res = requests.get(url)
    data = res.json()
    if data["cod"] == 200:
        weather = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        speak(f"Current weather in {city} is {weather} with temperature {temp} degrees Celsius.")
    else:
        speak("Sorry, I couldn't find the weather for that city.")

# Core Commands
def processCommand(c):
    c = c.lower()

    if "open google" in c:
        webbrowser.open("https://google.com")
    elif "open facebook" in c:
        webbrowser.open("https://facebook.com")
    elif "open youtube" in c:
        webbrowser.open("https://youtube.com")
    elif "open linkedin" in c:
        webbrowser.open("https://linkedin.com")

    elif c.startswith("play"):
        song = c.split("play")[-1].strip()
        if song in musicLibrary.music:
            webbrowser.open(musicLibrary.music[song])
        else:
            webbrowser.open(f"https://www.youtube.com/results?search_query={song}")

    elif "weather in" in c:
        city = c.split("weather in")[-1].strip()
        get_weather(city)

    elif "what's the time" in c or "time" in c:
        now = datetime.now().strftime("%H:%M")
        speak(f"The time is {now}")

    elif "what's the date" in c or "date" in c:
        today = datetime.now().strftime("%d %B %Y")
        speak(f"Today is {today}")

    elif "news" in c:
        r = requests.get(f"https://newsapi.org/v2/top-headlines?country=in&apiKey={newsapi}")
        if r.status_code == 200:
            data = r.json()
            articles = data.get('articles', [])[:5]
            for article in articles:
                speak(article['title'])

    elif "take a note" in c:
        speak("What should I note?")
        with sr.Microphone() as source:
            audio = recognizer.listen(source)
            note = recognizer.recognize_google(audio)
            write_note(note)

    elif "read my notes" in c:
        read_notes()

    elif "exit" in c or "shutdown" in c:
        speak("Shutting down. Goodbye.")
        exit()

    else:
        output = aiProcess(c)
        speak(output) 

# Main Loop
if __name__ == "__main__":
    speak("Initializing Alexa....")
    while True:
        r = sr.Recognizer()
        print("recognizing...")

        try:
            with sr.Microphone() as source:
                print("Listening...")
                audio = r.listen(source, timeout=5, phrase_time_limit=3)
            word = r.recognize_google(audio)
            if word.lower() == "alexa":
                speak("Haan, boliye")
                with sr.Microphone() as source:
                    print("Alexa Active...")
                    audio = r.listen(source)
                    command = r.recognize_google(audio)
                    processCommand(command)

        except Exception as e:
            print("Error; {0}".format(e))
