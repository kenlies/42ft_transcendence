import os
import signal
from .config import Config

def handle_sigstop(sig, frame):
	Config.openEditor = True
	
def handle_sigint(sig, frame):
	os.system('clear')
	os.system('stty echo')
	print("Goodbye!")
	os._exit(0)

signal.signal(signal.SIGINT, handle_sigint)
