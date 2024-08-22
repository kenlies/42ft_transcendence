import os
import time
import json
import signal
import asyncio
import datetime
import websockets
from datetime import timedelta
from .start_game import online_room
from .config import Config, init_ssl_context
from .utils_and_signals import handle_sigstop
from .print_banners_docs import print_banner, print_available_commands, print_live_chat_help

async def connect_to_match(invite_url):
	ssl_context = init_ssl_context()
	async with websockets.connect(invite_url, ssl=ssl_context) as ws:
		Config.currentWebSocket = ws
		await online_room(ws)
		await ws.close()
		Config.currentWebSocket = None

def check_invite_time(invite_time_str):
	invite_datetime = datetime.datetime.strptime(invite_time_str, "%Y-%m-%d %H:%M:%S")
	invite_datetime += timedelta(hours=3)
	current_datetime = datetime.datetime.now()
	time_difference = current_datetime - invite_datetime
	return time_difference < datetime.timedelta(minutes=3)

def private_message_editor(toChat):
	os.system('clear')
	print_banner()
	print("-----------------------------------------------------------------------------------------------------------------------")
	print("|                                                  MESSAGE EDITOR                                                     |")
	print("-----------------------------------------------------------------------------------------------------------------------")
	print("|  close            -  Close this editor                                                                              |")
	print("|  exit             -  Leave the chat                                                                                 |")
	print("|  accept           -  Accept a game invite                                                                           |")
	print("|  Type something and press enter to send a message to the chat!                                                      |")
	print("-----------------------------------------------------------------------------------------------------------------------")
	print("")
	print("")
	print("")
	os.system('stty echo')
	userInput = input("~Editor: ")
	if userInput == "close":
		load_chat(toChat)
		return "close"
	elif userInput == "exit":
		os.system('stty echo')
		return "exit"
	elif userInput == "accept":
		try:
			if Config.currentInviteUrl != "":
				invite_url = Config.currentInviteUrl
				if ("/online/" in invite_url):
					asyncio.get_event_loop().run_until_complete(connect_to_match(invite_url))
					Config.currentInviteUrl = ""
				else:
					print("Invalid invite URL.")
				return "close"
		except:
			print("Invite expired.")
			return "close"
	else:
		Config.session.post(Config.flowUrl + "/api/message", headers={"Content-Type": "application/json", "X-CSRFToken": Config.session.cookies["csrftoken"], "session-id": Config.session.cookies["sessionid"], "Referer": Config.flowReferer}, data=json.dumps({"receiver": toChat, "content": userInput}), verify=False)
		load_chat(toChat)
		return "sent"

def load_chat(toChat):
	response = Config.session.get(f"{Config.flowUrl}/api/message?other={toChat}", headers={"Content-Type": "application/json", "X-CSRFToken": Config.session.cookies["csrftoken"], "session-id": Config.session.cookies["sessionid"], "Referer": Config.flowReferer}, verify=False)
	response.raise_for_status()
	messages = response.json()
	os.system('stty -echo')
	os.system('clear')
	print_banner()
	print_available_commands()
	print_live_chat_help()
	print("chatting with " + toChat + "...")
	print("-----------------------------------------------------------------------------------------------------------------------")
	print("|                                                         CHAT                                                        |")
	print("-----------------------------------------------------------------------------------------------------------------------")
	print("|                                                                                                                     |")
	if messages is not []:
		for message in messages:
			if message["sender"] == Config.username:
				print("  You: " + message["content"])
			else:
				print("  " + message["sender"] + ": " + message["content"])
	else:
		print("  No messages with " + toChat + " yet.")
	print("|                                                                                                                     |")
	print("-----------------------------------------------------------------------------------------------------------------------\n")
	if messages is not []:
		for message in reversed(messages):
			if message["sender"] != Config.username and message["content"].startswith("GAME_INVITE="):
				if check_invite_time(message["date"]):
					print("You have received a game invite from " + message["sender"] + ". You can accept it in the editor.")
					Config.currentInviteUrl = message["content"].split("=")[1]
				break

def chat():
	signal.signal(signal.SIGTSTP, handle_sigstop)
	os.system('clear')
	Config.openEditor = False
	print_banner()
	print_available_commands()
	print("Getting your friends list...\n")
	response = Config.session.get(Config.flowUrl + "/api/user?username=" + Config.username, headers={"Content-Type": "application/json", "X-CSRFToken": Config.session.cookies["csrftoken"], "session-id": Config.session.cookies["sessionid"], "Referer": Config.flowReferer}, verify=False)
	response.raise_for_status()
	blockedByUs = response.json()["blocked"]
	toPrintFriends = response.json()["friends"]
	for user in blockedByUs:
		if user in toPrintFriends:
			toPrintFriends.remove(user)
	if toPrintFriends == []:
		toPrintFriends = ["No friends yet."]
	print("-----------------------------------------------------------------------------------------------------------------------")
	print("|                                                     MY FRIENDS                                                      |")
	print("-----------------------------------------------------------------------------------------------------------------------")
	print("|                                                                                                                     |")
	for friend in toPrintFriends:
		print("  " + friend)
	print("|                                                                                                                     |")
	print("-----------------------------------------------------------------------------------------------------------------------\n")
	if toPrintFriends[0] == "No friends yet.":
		print("No friends to chat with. Please add friends to chat.\n")
		return
	toChat = input("Enter the username of the friend you would like to chat with: ")
	if toChat not in toPrintFriends:
		print("Invalid friend. Please try again.\n")
		return
	load_chat(toChat)
	lastRefresh = time.time()
	while True:
		if Config.openEditor:
			userInput = private_message_editor(toChat)
			if userInput == "close":
				Config.openEditor = False
				continue
			elif userInput == "exit":
				os.system('clear')
				print_banner()
				print_available_commands()
				break
			Config.openEditor = False
		currentTime = time.time()
		if currentTime - lastRefresh > 1:
			load_chat(toChat)
			lastRefresh = currentTime 
