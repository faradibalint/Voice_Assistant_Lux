#core of the voice assistant
#contains function used to recognise/analyse voice commands and call suitable functions accordingly
#contains log handling functions
#runs in background repetedly listening for voice commands
#incorporates basic functions for system management
#noise reduction --> not working / under developement

from os import execv
from sys import executable, argv
from speech_recognition import WaitTimeoutError, UnknownValueError, Microphone, Recognizer, AudioData
from homeassistant_api import Client
from concurrent.futures import ThreadPoolExecutor
from traceback import format_exc
from csv import reader
from datetime import datetime
from time import sleep
from functions import *
from configuration.config import configuration_data, NUM
from global_vars import TABLE, CALLING
from response import response
from pydub import AudioSegment
from io import BytesIO

r = Recognizer()
m = Microphone()

def main():
    listen_background()


def writeToErrorLog(message):
    with open("log/sa_errorlog.txt", "a") as errorlog:
        errorlog.write("---------------------------------------------------------------------------------------\n")
        errorlog.write(str(datetime.now())+" - "+(str(message)))
        errorlog.write("---------------------------------------------------------------------------------------\n")
        
def defaultResponse() -> bool: # called when the "name" of the assistant is recognised, starts the process of listening for voice commands
    Place = -1
    Entity = -1
    Action = -1
    tries  = 0
    previous = ""
    while (Place == -1 or Entity == -1 or Action == -1) and tries < 3:
        try:
            temp = recursiveListen()
            if temp == True: return True
            elif temp == False: return False
            else:
                lower = previous + " " + temp           
                tries += 1
                print(lower)
                if not ActionCall(lower):
                    with ThreadPoolExecutor(max_workers=3) as executor:
                        Place = executor.submit(getPlace,lower,Place).result()
                        Entity = executor.submit(getDevice,lower,Entity).result()
                        Action = executor.submit(getAction,lower,Action).result()
                    print(Place,Entity,Action)
                    if Place !=-1 and Entity !=-1 and Action!=-1:
                        Alias = getDeviceID(Place,Entity,lower)
                        if Alias:
                            print(Alias)
                            if execute(Entity, Action, Alias, lower):
                                return True
                        else:
                            return True
                    elif Place!=-1 and Entity!=-1 and Action==-1:
                        response("Nem értettem pontosan. Mit szeretnél csinálni az eszközzel?")
                        previous = lower
                    elif Place!=-1 and Entity==-1 and Action!=-1:
                        response("Nem értettem pontosan. Melyik eszközt szeretnéd használni?")
                        previous = lower
                    elif Place==-1 and Entity!=-1 and Action!=-1:
                        response("Nem értettem pontosan. Melyik helyiségben van az eszköz?")
                        previous = lower
                    else:
                        response("Nem sikerült megérteni a kérést. Próbáld újra!")
                        return True
                else:
                    return True
        except WaitTimeoutError:
            response("Nem hallottam kérést")
            return True
        except UnknownValueError:
            response("Nem hallottam kérést")
            return True
        except Exception as e:
            response("Hiba lépett fel. Hibakód jegyezve. Próbálkozz újra.")
            writeToErrorLog(str(e) + "\n" + format_exc())
            return True

    return True
def recursiveListen(): # performs input correction when a voice command cannot be totally understood
    try:
        audio = Listen(True)
        recognized_text = r.recognize_google(audio,language='hu-HU')
        lower = recognized_text.lower()
    except WaitTimeoutError:
        pass
    for key, values in configuration_data.items():
                if key.startswith("Operation"):
                    for value in values:
                        if value in lower:
                            return operationCall(key)
    return lower
    
def getPlace(command,Place): # recognises the place where the entity intended to be controlled is located
    if Place ==-1:
        keys_found = []
        for key, values in TABLE.items():
            if isinstance(values, list):
                for value in values:
                    if value in command:
                        keys_found.append(key)
                        break
            else:
                if values in command:
                    keys_found.append(key)
        if keys_found:
            return keys_found
        else:
            return -1
    else:
        return Place


def getDevice(command,Entity): # recognises the type of entity intended to be controlled
    if Entity ==-1:
        for key, values in configuration_data.items():
            if key.startswith("Entity"):
                for value in values:
                    if value in command:
                        return key[7:]
        return -1
    else:
        return Entity

def getAction(command,Action): # recognises the type of action intended to be performed on an entity
    if Action ==-1:
        for key, values in configuration_data.items():
            if key.startswith("Controll"):
                for value in values:
                    if value in command.split():
                        if "SET" in key:
                            return [2,value]
                        elif "UP" in key:
                            return 1
                        elif "DOWN" in key:
                            return 0
        return -1
    else:
        return Action
    
def getDeviceID(place,entity,lower): #acquires the id of the device/devices intented to being controlled
    Alias = []
    with open('configuration/entity.csv','r',encoding='utf-8') as csvfile:
        ENTITY = reader(csvfile)
        for i in place:
            for row in ENTITY:
                if row[0] == i and row[1] == entity:
                    Alias.append([row[2],row[3]])
    if len(Alias)>1:
        counter = 0
        while counter < 3:
            if "összes" in lower or "mind" in lower:
                return Alias
            try:
                for j in Alias:
                    for k in j[1].split():
                        if k in lower:
                            return [j]
                response("Több eszközt is találtunk a megadott paraméterekkel. Melyiket szeretnéd irányítani?")
                try:
                    lower = recursiveListen()
                    counter+=1
                except WaitTimeoutError:
                    pass
            except Exception as e:
                writeToErrorLog(str(e) + "\n" + format_exc())
                response("Hiba lépett fel. A hiba oka jegyezve.")
    elif len(Alias) == 1:
        return Alias
    else:
        response("Nem sikerült megtalálni az eszközt. Próbáld újra.")
        return []

def execute(entity, action, alias, command) -> bool: #calls for the exact function needed to execute voice command
    if action == 1:
        if entity =="light" or entity =="led":
            if turnDeviceOn(alias,"light"):
                response("Lámpák sikeresen felkapcsolva")
                return True
            else:
                response("A lámpákat nem sikerült felkapcsolni. Hibakód jegyezve")
                return False
        elif entity == "climate":
            if turnDeviceOn(alias,entity):
                response("A klíma sikeresen bekapcsolva")
                return True
            else:
                response("A klímát nem sikerült bekapcsolni. Hibakód jegyezve.")
                return False
        elif entity == "cover":
            if ShutterOpen(alias):
                response("A redőnyök sikeresen felhúzva")
                return True
            else:
                response("A redőnyöket nem sikerült felhúzni")
                return False
        elif entity == "switch":
            if turnDeviceOn(alias,entity):
                response("A switch sikeresen bekapcsolva")
                return True
            else:
                response("A switchet nem sikerült bekapcsolni. Hibakód jegyezve.")
                return False
        '''elif entity == "tv":
            if turnTVpower(alias):
                response("A tv sikeresen bekapcsolva")
                return True
            else:
                response("A tv nem sikerült bekapcsolni")
                return False'''
    elif action == 0:
        if entity =="light" or entity =="led":
            if turnDeviceOff(alias,"light"):
                response("Lámpák sikeresen lekapcsolva")
                return True
            else:
                response("A lámpákat nem sikerült lekapcsolani. Hibakód jegyezve")
                return False
        elif entity == "climate":
            if turnDeviceOff(alias,entity):
                response("A klíma sikeresen kikapcsolva")
                return True
            else:
                response("A klímát nem sikerült kikapcsolni. Hibakód jegyezve.")
                return False
        elif entity == "cover":
            if ShutterClose(alias):
                response("A redőnyök sikeresen lehúzva")
                return True
            else:
                response("A redőnyöket nem sikerült lehúzni")
                return False
        elif entity == "switch":
            if turnDeviceOff(alias,entity):
                response("A switch sikeresen kikapcsolva")
                return True
            else:
                response("A switchet nem sikerült kikapcsolni. Hibakód jegyezve.")
                return False
        '''elif entity == "tv":
            if turnTVpower(alias):
                response("A tv sikeresen kikapcsolva")
                return True
            else:
                response("A tv nem sikerült kikapcsolni")
                return False'''
    elif action[0] == 2:
        if entity == "light" or entity =="led":
            return setLight(action, alias, command)
        elif entity == "cover":
            return setCover(action, alias, command)
        elif entity == "climate":
            return setClimate(action, alias, command)

def operationCall(key): # used to call system funtions
    if "ESCAPE" in key:
        response("Viszlát!")
        return False
    elif "REBOOT" in key:
        response("Újraindítás")
        execv(executable, ['python3'] + argv)
    elif "DELLOG" in key:
        try:
            clearErrorLog()
        except Exception as e:
            writeToErrorLog(str(e) + "\n" + format_exc())
            response("Nem sikerült törölni a log-ot. Hiba jegyezve")
        else:
            response("A hibalog sikeresen törölve")
            return True

    
def ActionCall(text) -> bool: # used when voice command is not connected to a room 
    action_todo = ""
    for key, values in configuration_data.items():
            if key.startswith("Action"):
                for value in values:
                    if value in text:
                        action_todo = key[7:]
    if action_todo != "":
        if action_todo == "music":
            Action = -1
            Action = getAction(text,Action)
            if Action == -1:
                response("Nem értettem pontosan. Próbáld újra.")
                return True
            callMusic(Action)
            return True
        elif action_todo == "termostat":
            callTermostat(text)
            return True
        elif action_todo == "quarantine":
            Quarantine(text)
            return True
        elif action_todo == "weather":
            action = -1    # ha még valahova kell majd az action lekérdezése akkor az mehet az ifenkívül az egész függvény elejére.
            action = getAction(text,action)
            if action == -1:
                getWeather(text)
            else:
                return False
            return True
        elif action_todo == "phonecall":
            phoneCall(text)
            return True
        # ide mehetnek elifbe az actionok 
    else:
        return False
def Quarantine(text): # performs a "quarantine" operation that blocks the  listetning of the microphone in the background for a certain amount of time
    for i in text.split():
        if i.isdigit():
            if "másodperc" in text:
                response("Karantén kezdődik")
                sleep(int(i))
            elif "perc" in text:
                response("Karantén kezdődik")
                sleep(int(i)*60)
            else:
                response("Karantén kezdődik")
                sleep(int(i))
            response("Karantén vége")
        elif i in NUM and i.isalpha():
            if "másodperc" in text:
                response("Karantén kezdődik")
                sleep(NUM.get(i))
            elif "perc" in text: 
                response("Karantén kezdődik")
                sleep(NUM.get(i)*60)
            else:
                response("Karantén kezdődik")
                sleep(NUM.get(i))
            response("Karantén vége")

def clearErrorLog():
    open('log/sa_errorlog.txt', 'w').close()
    
def listen_background() -> None: # core function --> runs the repeated listening in the background until interrupted
    response("A program elindult")
    while True:
        try:
            audio = Listen() # records audio from microphone and stores it in audio variable
            try:
                recognized_text = r.recognize_google(audio_data=audio, language='hu-HU') # performs speech recognition
                #recognized_text = r.recognize_google(audio, language='hu-HU')
            except Exception as e:
                print(e)
                pass
            else:
                Process(recognized_text) # if the audio could be recognised this call starts to process it

        except WaitTimeoutError:
            print("WaitTimeoutError")
            pass
        except Exception as e:
            writeToErrorLog(str(e) + "\n" + format_exc())
            exit()

def Listen(isrecursive = False):
    with m as source:
        print(r.energy_threshold) # used for debugging / adjustion --> monitor recquired
        r.adjust_for_ambient_noise(source, 0.5)
        audio_data = r.listen(source, None, 10)
        #noise reduction
        reduction_strength = 10
        try:
            noise_reduced_audio = apply_noise_reduction(audio_data, reduction_strength)
            #file_path = "recorded_audio1.wav"
            #with open(file_path, "wb") as file:
                #file.write(audio_data.get_wav_data())  
        except Exception as e:
            print(e)
        return noise_reduced_audio

def Process(recognized_text): # processs the recognised audio looking for a wake call 
    lower = recognized_text.lower()
    print(lower)
    for call in CALLING: # checks for wake words defined in saconfig.txt
        if call in lower:
            response("",True) # basic response when waked
            if not defaultResponse():
                import sys
                sys.exit()    
            break

def apply_noise_reduction(audio_data, reduction_strength):
    
    audio_segment = AudioSegment.from_file_using_temporary_files(BytesIO(audio_data.get_wav_data()), format="wav")
    noise_reduced_audio = audio_segment - reduction_strength
    output_buffer = BytesIO()
    noise_reduced_audio.export(output_buffer, format="wav")
    noise_reduced_audio_data = AudioData(output_buffer.read(), audio_data.sample_rate, audio_data.sample_width)

    return noise_reduced_audio_data

if __name__ == "__main__":
    main()



