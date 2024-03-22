import pyttsx3
import speech_recognition as sr
import datetime
from pyautogui import press
import requests

class WeatherService(object):
    API_URL = "http://api.openweathermap.org/data/2.5/weather?q={}&APPID={}&units=metric"
    API_KEY = "3b31a7e394e41c3a30759dfde1a3383e"
    
    def __init__(self):
        pass

    def get_weather_data(self, city_name):
        r = requests.get(WeatherService.API_URL.format(city_name, WeatherService.API_KEY))
        weather_data = (r.json())
        temp = self._extract_temp(weather_data)
        description = self._extract_desc(weather_data)
        return "Currently, in {}, its {} degrees with {}".format(city_name, temp, description)
    
    def _extract_temp(self, weatherdata):
        temp = weatherdata['main']['temp']
        return temp

    def _extract_desc(self, weatherdata):
        return weatherdata['weather'][0]['description']

class voiceAssistant:
    def __init__(self) -> None:
        self.engine = pyttsx3.init('sapi5')
        self.voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', self.voices[1].id)
        self.check = True
        self.checkCommand = True
        self.count = 0
        self.time1 = 0
        self.time2 = 0
        self.commandStatus = False

    def speak(self,audio) -> None:
        self.engine.say(audio)
        self.engine.runAndWait()
    
    def activateAssistant(self) -> None:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            audio = r.record(source, duration = 3, offset = None)
        try:
            self.check = True
            query = r.recognize_google(audio, language='en-in')
            query = query.lower()
        except Exception as e:
            return "None"
        return query

    def takeCommand(self) -> None:
        self.commands = [
            'help',
            'start navigation',
            'stop navigation',
            'day',
            'exit',
            'increase volume',
            'decrease volume',
            'time',
            'weather'
            ]
        r = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                print("Listening...")
                audio = r.listen(source, timeout = 3, phrase_time_limit=5)
            print("Recognizing...")    
            userQuery = r.recognize_google(audio, language='en-in')
            userQuery = userQuery.lower()
            for i in self.commands:
                if(i in userQuery):
                    return userQuery
        except:
            pass
        if self.count < 2: self.speak("Say that again please...")
        else: self.speak("sorry try again....")
        self.count += 1
        return " "

    def run(self) -> None:
        f = open("voice.txt", "r")
        self.speak(f.read())
        f.close()

    def get_ip(self):
        self.response = requests.get('https://api64.ipify.org?format=json').json()
        return self.response["ip"]

    def get_location(self):
        ip_address = self.get_ip()
        self.response = requests.get(f'https://ipapi.co/{ip_address}/json/').json()
        return self.response.get("city") 

    def main(self) -> None:
        while True:
            if self.commandStatus:
                self.run()
            if("hello" in self.activateAssistant()):
                print("Assistant Started")
                now = datetime.datetime.now()
                hour = now.hour
                if(hour>5 and hour<12):
                    self.speak("good morning  ")
                elif(hour>=12 and hour<18):
                    self.speak("good afternoon  ")
                else:
                    self.speak("good evening  ")                    
                while self.check:
                    userQuery = self.takeCommand().lower()
                    print(f"User Query: {userQuery}")
                    if self.count > 2:
                        self.count = 0
                        self.check = False

                    elif('help' in userQuery):
                        self.count = 0
                        print("Available commands: ")
                        self.speak("Available commands")
                        for x in self.commands:
                            print(x)
                            self.speak(x)

                    elif('start navigation' in userQuery):
                        self.count = 0
                        print("Starting Navigation")
                        self.speak("starting navigation")
                        f = open("state.txt", "w")
                        f.write("True")
                        f.close()
                        self.commandStatus = True
                        self.check = False

                    elif('stop navigation' in userQuery):
                        self.count = 0
                        self.commandStatus = False
                        print("Exiting navigation")
                        self.speak("exiting Navigation")
                        f = open("state.txt", "w")
                        f.write("")
                        f.close()
                        self.check = False

                    elif('day' in userQuery):
                        self.count = 0
                        day = datetime.datetime.today().strftime("%A")
                        print(day)
                        self.speak(day)
                        self.check = False
                    
                    elif ("increase volume" in userQuery):
                        self.count = 0
                        press("volumeup")
                        press("volumeup")
                        press("volumeup")

                    elif ("decrease volume" in userQuery):
                        self.count = 0
                        press("volumedown")
                        press("volumedown")
                        press("volumedown")

                    elif('time' in userQuery):
                        self.count = 0
                        now = datetime.datetime.now()
                        hour = now.hour
                        minute = now.minute
                        print(f"Time is {hour} hour and {minute} minutes")
                        self.speak(f"Time is {hour} hour and {minute} minutes")
                        self.check = False

                    elif('weather' in userQuery):    
                        self.count = 0
                        wetherObj = WeatherService()
                        #city = self.get_location()
                        city = 'changa'
                        weatherdata = wetherObj.get_weather_data(city)
                        print(weatherdata)
                        self.speak(weatherdata)
                        self.check = False

                    elif('exit' in userQuery):
                        print("Assistant Exited")
                        self.check = False

if __name__ == "__main__":
    obj = voiceAssistant()
    obj.main()