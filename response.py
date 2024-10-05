def response(text,isDefault = False) -> None: # uses the default respnse file after wake call or custom response according to event
    if isDefault: # default wake response
        init()
        mixer.init()
        try:
            mixer.music.load(DEFRESPONSE) #ownership bug needs to be examined
            mixer.music.play()
        except Exception as e:
            writeToErrorLog(str(e) + "\n" + format_exc())
    else:
        try: # custom response generation
            get_event_loop().run_until_complete(_main(text))
        except Exception as e:
            writeToErrorLog(str(e) + "\n" + format_exc())
         
async def _main(TEXT) -> None: # generates custom response
    try:
        communicate = Communicate(TEXT, VOICE)
        await communicate.save(OUTPUT_FILE)
        init()
        mixer.init()
        mixer.music.load(OUTPUT_FILE)
        mixer.music.play()
        while mixer.music.get_busy():
            time.Clock().tick(10)
        mixer.music.unload()
    except Exception as e:
        writeToErrorLog(str(e) + "\n" + format_exc())

def writeToErrorLog(message):
    with open("log/sa_errorlog.txt", "a") as errorlog:
        errorlog.write("---------------------------------------------------------------------------------------\n")
        errorlog.write(str(datetime.now())+" - "+(str(message)))
        errorlog.write("---------------------------------------------------------------------------------------\n")
        
if not __name__ == "__main__":
    from global_vars import VOICE, OUTPUT_FILE, DEFRESPONSE
    from edge_tts import Communicate
    from asyncio import get_event_loop
    from pygame import mixer, init, time
    from traceback import format_exc
    from datetime import datetime
    