# Voice_Assistant_Lux
 Hungarian voice assistant for Home Assistant based smart homes
 Beta version - Tested on Lenovo Thinkpad T580 with HA on Raspberry Pi (the project communicates with HA via external link (can be used via local network too))

 -Uses Homeassistant API a pythonic module that interacts with Homeassistant’s REST API integration. (https://homeassistantapi.readthedocs.io/en/latest/)
 -Uses SpeechRecognition Python lib to perform speech recognition via Google Speech Recognition (The library supports multiple speech recognition services including offline ones too --> the project can be modified to use OFFLINE speech recognition) (https://pypi.org/project/SpeechRecognition/)
 -Uses edge-tts a Python module that allows you to use Microsoft Edge's online text-to-speech service. The project's voice response feature relies on this library.
 -There are initial steps to reduce noise on the recorded audio --> Should be used/ignored according to custom microphone quality.
 
 
 
