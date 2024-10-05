#starts the main file in the background
from subprocess import Popen

def execute_main_pyw():
    file_path = r'C:\Test\main.py' # Path to main.py
    try:
        Popen(['start', 'pythonw', file_path], shell=True) # use 'python' for console (can be used for debugging) / 'pythonw' for background execution
    except:
        pass
if __name__ == "__main__":
    execute_main_pyw()