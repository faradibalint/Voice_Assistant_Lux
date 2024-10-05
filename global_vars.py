#loads configuration data
def main():
    global URL
    global TOKEN
    global VOICE
    global OUTPUT_FILE
    global DEFRESPONSE
    global TABLE
    global CALLING

    with open('configuration/table.json', 'r',encoding='utf-8') as json_file:
        TABLE = load(json_file)

    with open("configuration/saconfig.txt", 'r', encoding='utf8') as f:
        data = f.readlines()
        CALLING = data[0].strip().split()
        URL = data[1].strip()
        TOKEN = data[2].strip()
        VOICE = data[3].strip()
        OUTPUT_FILE = data[4].strip()
        DEFRESPONSE = data[5].strip()

if not __name__ == "__main__":
    from json import load
    main()