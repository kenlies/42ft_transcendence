import os
import signal
import asyncio
from .config import Config

async def receive_no_wait(websocket):
	recv_task = asyncio.create_task(websocket.recv())
	try:
		done = await asyncio.wait_for(recv_task, timeout=0.01)
		if len(done) == 0:
			return None
		return done
	except asyncio.TimeoutError:
		return None

def handle_sigstop(sig, frame):
	Config.openEditor = True
	
def handle_sigint(sig, frame):
	os.system('clear')
	os.system('stty echo')
	print("Goodbye!")
	os._exit(0)

signal.signal(signal.SIGINT, handle_sigint)
