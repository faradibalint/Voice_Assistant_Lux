def turnDeviceOn(Alias,entity) -> bool:
    try:
        client = Client(URL, TOKEN)
        service = client.get_domain(entity)
        for i in Alias:
            service.turn_on(entity_id=i[0])
        return True
    except Exception as e:
        writeToErrorLog(str(e) + "\n" + format_exc())
        return False

def turnDeviceOff(Alias,entity) -> bool:
    try:
        client = Client(URL, TOKEN)
        service = client.get_domain(entity)
        for i in Alias:
            service.turn_off(entity_id=i[0])
        return True
    except Exception as e:
        writeToErrorLog(str(e) + "\n" + format_exc())
        return False

def ShutterOpen(Alias) -> bool:
    try:
        client = Client(URL, TOKEN)
        service = client.get_domain("cover")
        for i in Alias:
            service.open_cover(entity_id=i[0])
        return True
    except Exception as e:
        writeToErrorLog(str(e) + "\n" + format_exc())
        return False

def ShutterClose(Alias) -> bool:
    try:
        client = Client(URL, TOKEN)
        service = client.get_domain("cover")
        for i in Alias:
            service.close_cover(entity_id=i[0])
        return True
    except Exception as e:
        writeToErrorLog(str(e) + "\n" + format_exc())
        return False

def setCover(action, Alias, command) -> bool: # sets the cover at a custom level
    try:
        client = Client(URL, TOKEN)
        service = client.get_domain("cover")
        command = command.split()
        counter = 0
        setTo = ""
        while setTo == "" and counter < 3:
            for i in command:
                if "%" in i:
                    setTo = i[:i.find("%")]
                elif "százalék" in i:
                    location = command.index(i)-1
                    if command[location].isdecimal():
                        setTo = command[location]
                    else:
                        try:
                            setTo = str(NUM[command[location]])
                        except:
                            setTo == ""
            if setTo == "":
                response("Nem értettem pontosan. Mit szeretnél csinálni a redőnnyel?")
                command = recursiveListen().split()
                counter+=1
        if setTo != "":
            setToo = (float(setTo)*(-0.8))+100
            try:
                for i in Alias:
                    service.set_cover_position(entity_id=i[0], position=setToo)
            except Exception as e:
                response("A redőnyt nem sikerült átállítani. Hibakód jegyezve")
                writeToErrorLog(str(e) + "\n" + format_exc())
                return False
            else:
                if setTo == "100":
                    response("A redőny sikeresen átállítva száz százalékra")
                else:
                    response("A redőny sikeresen átállítva"+setTo+"százalékra")
        else:
            response("A redőnyt nem sikerült átállítani. Próbáld újra!")
    except Exception as e:
        response("Hiba történt. A hiba jegyezve.")
        writeToErrorLog(str(e) + "\n" + format_exc())
    else:
        return True

def setLight(action, Alias, command) -> bool:  # sets color and brigtness of lights
    try:
        client = Client(URL, TOKEN)
        service = client.get_domain("light")
        changeColorTo = ""
        if "szín" in command:
            counter = 0
            while changeColorTo == "" and counter < 3:
                counter += 1
                for key,value in colorTable.items():
                    if key in command:
                        changeColorTo = key, value
                        break
                if changeColorTo:
                    try:
                        for i in Alias:
                            if changeColorTo[1] == [0, 0, 0, 255]:
                                service.turn_on(entity_id = i[0], rgbw_color = changeColorTo[1])
                            else:
                                service.turn_on(entity_id = i[0], color_name = changeColorTo[1])

                    except Exception as e:
                        response("A lámpa színét nem sikerült átállítani. Hibakód jegyezve")
                        writeToErrorLog(str(e) + "\n" + format_exc())
                        return False
                    else:
                        response("A lámpák színe sikeresen átállítva"+changeColorTo[0])
                else:
                    response("Nem értettem pontosan. MIlyen színre állítsam a lámpát?")
                    try:
                        command = recursiveListen()
                        counter+=1
                    except:
                        pass
        
        elif "fény" in command:
            command = command.split()
            counter = 0
            setTo = ""
            while setTo == "" and counter < 3:
                for i in command:
                    if "%" in i:
                        setTo = i[:i.find("%")]
                    elif "százalék" in i:
                        location = command.index(i)-1
                        if command[location].isdecimal():
                            setTo = command[location]
                        else:
                            try:
                                setTo = str(NUM[command[location]])
                            except:
                                setTo = ""
                if setTo == "":
                    response("Nem értettem pontosan. Mit szeretnél csinálni a fényerővel?")
                    command = recursiveListen().split()
                    counter+=1    
            for i in Alias:
                try:
                    bright = int(client.get_state(entity_id=i[0]).attributes["brightness"])
                except Exception as e:
                    response("Nem sikerült lekérni a lámpa adatait.")
                    writeToErrorLog(str(e) + "\n" + format_exc())
                    return False
                if "növ" in action[1]:
                    if int(bright/255*100) + int(setTo) > 100:
                        brightTo = brightTo = list(NUM.keys())[list(NUM.values()).index(100)]
                    else:
                        brightTo = int(bright/255*100) + int(setTo)
                    try:
                        service.turn_on(entity_id = i[0], brightness = bright + 255*float(int(setTo)/100))
                    except Exception as e:
                        response("A lámpák fényerejét nem sikerült növelni. Hibakód jegyezve")
                        writeToErrorLog(str(e) + "\n" + format_exc())
                        return False
                    else:
                        response("A lámpák fényereje sikeresen növelve"+str(brightTo)+"százalékra")
                elif "csök" in action[1]:
                    if int(bright/255*100) - int(setTo) < 0:
                        brightTo = 0
                    else:
                        brightTo = int(bright/255*100) - int(setTo)
                    try:
                        service.turn_on(entity_id = i[0], brightness = bright - 255*float(int(setTo)/100))
                    except Exception as e:
                        response("A lámpák fényerejét nem sikerült csökkenteni. Hibakód jegyezve")
                        writeToErrorLog(str(e) + "\n" + format_exc())
                        return False
                    else:
                        response("A lámpák fényereje sikeresen csökkentve"+str(brightTo)+"százalékra")
                else:
                    if int(setTo) < 0:
                        brightTo = 0
                    elif int(setTo) > 100:
                        brightTo = list(NUM.keys())[list(NUM.values()).index(100)]
                    else:
                        brightTo = int(setTo)
                    try:
                        service.turn_on(entity_id = i[0], brightness = 255*float(int(setTo)/100))
                    except Exception as e:
                        response("A lámpák fényerejét nem sikerült átállítani. Hibakód jegyezve")
                        writeToErrorLog(str(e) + "\n" + format_exc())
                        return False
                    else:
                        response("A lámpák fényereje sikeresen beállítva"+str(brightTo)+"százalékra")

    except Exception as e:
        response("Hiba történt. A hiba jegyezve.")
        writeToErrorLog(str(e) + "\n" + format_exc())
    else:
        return True

'''
def turnTVpower(Alias):
    from samsungtv import SamsungTV
    for i in Alias:
        try:
            tv = SamsungTV(i[0])
            tv.power()
        except Exception as e:
            writeToErrorLog(str(e) + "\n" + format_exc())
            return False
        else:
            return True
'''        
def setClimate(action, alias, command) -> bool: # sets climate tempreture to a custom value
    try:
        client = Client(URL, TOKEN)
        service = client.get_domain("climate")
        for i in command.split():
            if i.isdigit():
                setTo = int(i)
            elif i in NUM and i.isalpha():
                setTo = NUM.get(i)
        if setTo > 15 and setTo < 30:
            try:
                client = Client(URL, TOKEN)
                service = client.get_domain("climate")
                for i in alias:
                    service.set_temperature(entity_id = i[0], temperature = setTo)
            except Exception as e:
                response("Nem sikerült beállítani a hőmérsékletet. Hiba jegyezve.")
                writeToErrorLog(str(e) + "\n" + format_exc())
            else:
                response("Klíma Sikeresen átállítva" + str(setTo) + "fokra")
    except Exception as e:
        response("Hiba történt. A hiba jegyezve.")
        writeToErrorLog(str(e) + "\n" + format_exc())
    else:
        return True

def callTermostat(text):
    with open('configuration/entity.csv','r',encoding='utf-8') as csvfile:
        ENTITY = reader(csvfile)
        Alias =  []
        for row in ENTITY:
            if row[1] == "termostat":
                Alias.append([row[2],row[3]])
        for i in text.split():
            if i.isdigit():
                setTo = int(i)
            elif i in NUM and i.isalpha():
                setTo = NUM.get(i)
        if setTo > 15 and setTo < 30:
            try:
                client = Client(URL, TOKEN)
                service = client.get_domain("climate")
                for i in Alias:
                    service.set_temperature(entity_id = i[0], temperature = setTo)
            except Exception as e:
                response("Nem sikerült beállítani a hőmérsékletet. Hiba jegyezve.")
                writeToErrorLog(str(e) + "\n" + format_exc())
            else:
                response("Hőmérséklet Sikeresen átállítva" + str(setTo) + "fokra")
        else:
            response("Nem megfelelő paraméter. Próbáld újra")
def callMusic(Action):  # uses Onkyo receiver on local network to turn on/off radio, controll the volume
    if Action == 1:
        try:
            with eISCP('192.168.x.y') as receiver: # TODO: check if 192.168.x.y is correct --> read IP from configuration file / find receiver automatically on local network
                receiver.command('power on')
                sleep(3)
                try:# TODO! itt azért kell mindig az except ágban folytani mert a függvény mindig TO- errort ad vissza ?? miért
                    receiver.raw('SLI2B') # LOW level eISCP commands for Onkyo receiver
                    receiver.raw('NSV0E0')
                except:
                    try: # 2 enter would be sufficient but due to input/processing lag on onkyo 3 is needed
                        receiver.raw('OSDENTER')
                    except:
                        try:
                            receiver.raw('OSDENTER')
                        except:
                            pass 
        except Exception as e:
            writeToErrorLog(str(e) + "\n" + format_exc())
            response("Nem sikerült bekapcsolni a rádiót. Hiba jegyezve.")
        else:
            response("Rádió sikeresen bekapcsolva")
    elif Action == 0:
        try:
            with eISCP('192.168.x.y') as receiver:
                receiver.command('power off')
        except Exception as e:
            writeToErrorLog(str(e) + "\n" + format_exc())
            response("Nem sikerült kikapcsolni a rádiót. Hiba jegyezve.")
        else:
            response("Rádió sikeresen kikapcsolva")
    elif Action[0] == 2:
        if "csökk" in Action[1] or "növ" in Action[1] or "hang" in Action[1] or "halk" in Action[1]:
            try:
                with eISCP('192.168.x.y') as receiver:
                    resp = receiver.raw('MVLQSTN')
                    if resp.startswith('MVL'):
                        try:
                            volume_level = int(resp[3:],16)
                            if "csökk" in Action[1] or "halk" in Action[1]:
                                volume_level -=5
                                receiver.command("volume "+str(volume_level))
                            elif "növ" in Action[1] or "hang" in Action[1]:
                                volume_level +=5
                                receiver.command("volume "+str(volume_level))
                        except Exception as e:
                            writeToErrorLog(str(e) + "\n" + format_exc())
                            response("Nem sikerült beállítani a hangerőt. Hiba jegyezve")
                    else:
                        response("Nem sikerüt lekérdezni a hangerőt. Hiba jegyezve")
                        writeToErrorLog(str(e) + "\n" + format_exc())
            except Exception as e:
                writeToErrorLog(str(e) + "\n" + format_exc())
                response("Nem sikerült kommunikálni az erősítővel. Hiba jegyezve.")
            else:
                response("Hangerő átállítva")
        pass
        #ha valamit állítani akarunk a zenén

def getWeather(text):
    try:
        if "holnap" in text:
            client = Client(URL, TOKEN)
            temperature = client.get_state(entity_id='weather.otthon').attributes["forecast"][0]["temperature"]
            wind = client.get_state(entity_id='weather.otthon').attributes["forecast"][0]["wind_speed"]
            if int(wind)<10:
                response("A hőmérséklet körülbelül {fok} fok lesz, számottevő szél nincs".format(fok=int(temperature))) 
            elif int(wind)>10:
                response("A hőmérséklet körülbelül {fok} fok lesz, a szél meghaladhatja a 10 km per órát".format(fok=int(temperature)))
            elif int(wind)>20:
                response("A hőmérséklet körülbelül {fok} fok lesz, erős szélre kell számítani, ami meghaladhatja a 20 km per órát".format(fok=int(temperature)))
            else:
                response("A hőmérséklet körülbelül {fok} fok lesz, a szél meghaladhatja a {szel} km per órát".format(fok=int(temperature),szel=int(wind)))
        else:
            client = Client(URL, TOKEN)
            temperature = client.get_state(entity_id='weather.otthon').attributes["temperature"]
            wind = client.get_state(entity_id='weather.otthon').attributes["wind_speed"]
            if int(wind)<10:
                response("A hőmérséklet körülbelül {fok} fok, számottevő szél nincs".format(fok=int(temperature))) 
            elif int(wind)>10:
                response("A hőmérséklet körülbelül {fok} fok, a szél meghaladhatja a 10 km per órát".format(fok=int(temperature)))
            elif int(wind)>20:
                response("A hőmérséklet körülbelül {fok} fok, erős szélre kell számítani, ami meghaladhatja a 20 km per órát".format(fok=int(temperature)))
            else:
                response("A hőmérséklet körülbelül {fok} fok, a szél meghaladhatja a {szel} km per órát".format(fok=int(temperature),szel=int(wind)))
    except Exception as e:
        writeToErrorLog(str(e) + "\n" + format_exc())
        response("Nem sikerült lekérni az indőjárás adatokat. Hiba jegyezve")

def phoneCall(text):
    try:
        client = Client(URL, TOKEN)
        service = client.get_domain("script")
        if "xy" in text:
            try:
                service.telefon_xy() 
            except Exception as e:
                response("Nem sikerült felhívni xy-t. Hiba jegyezve")
                writeToErrorLog(str(e) + "\n" + format_exc())
            else:
                response("xy felhívva")
        elif "xyz" in text:
            try:
                service.telefon_xyz() 
            except Exception as e:
                response("Nem sikerült felhívni xyz-t. Hiba jegyezve")
                writeToErrorLog(str(e) + "\n" + format_exc())
            else:
                response("xyz felhívva")
       
        else:
            try:
                service = client.get_domain("switch")
                service.turn_off(entity_id="switch.sonoff_xyz")
            except Exception as e:
                response("Ismeretlen szám vagy sikertelen vonalbontás. Hiba jegyezve")
                writeToErrorLog(str(e) + "\n" + format_exc())
            else:
                response("A vonal sikeresen bontva")

    except Exception as e:
        response("Hiba történt. A hiba jegyezve.")
        writeToErrorLog(str(e) + "\n" + format_exc())
    else:
        return True


if not __name__ == "__main__":
    from main import writeToErrorLog, recursiveListen
    from global_vars import URL, TOKEN
    from configuration.config import colorTable, NUM
    from homeassistant_api import Client
    from traceback import format_exc
    from response import response
    from eiscp import eISCP
    from csv import reader
    from time import sleep