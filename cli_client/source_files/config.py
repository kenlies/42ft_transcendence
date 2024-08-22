import re
import requests

class Config:
	session = requests.Session()
	wait_time = None
	flowUrl = None
	flowReferer = None
	openEditor = None
	currentWebSocket = None
	paddleSpeed = None
	username = None
	currentInviteUrl = None
	myRole = None
	game_state = None
	inputQueue = None
	
def init_globals(hostIp):
	Config.wait_time = 0.5
	Config.flowUrl = hostIp
	Config.flowReferer = re.sub(r':\d+$', '', hostIp)
	Config.openEditor = False
	Config.currentWebSocket = None
	Config.myRole = 0
	Config.username = ""
	Config.currentInviteUrl = ""
	Config.game_state = None
	Config.inputQueue = None
	response = Config.session.get(Config.flowUrl, timeout=3, verify=False)
	if (response.status_code != 200):
		raise Exception("Failed to connect to server.")
