import os
import json
import asyncio
from .config import Config
from .print_banners_docs import print_banner, print_live_chat_help

async def send_invite(ws):
	response = Config.session.get(Config.flowUrl + "/api/user?username=" + Config.username, headers={"Content-Type": "application/json", "X-CSRFToken": Config.session.cookies["csrftoken"], "session-id": Config.session.cookies["sessionid"], "Referer": Config.flowReferer}, verify=False)
	friends = response.json()["friends"]
	blocked = response.json()["blocked"]
	for user in blocked:
		if user in friends:
			friends.remove(user)
	if len(friends) == 0:
		print("You don't have any friends to invite.")
		await asyncio.sleep(Config.wait_time)
	else:
		print("Your friends list: ")
		for f in friends:
			print('  ' + f)
		while True:
			receiver = input("Enter the username of the friend you want to invite or cancel with 'c': ")
			if receiver == 'c' or receiver in friends:
				break
			else:
				print("Invalid username. Please try again.")
		if receiver != 'c':
			await ws.send(json.dumps({"type": "invite", "receiver": receiver}))

def online_editor():
	os.system('clear')
	print_banner()
	print("-----------------------------------------------------------------------------------------------------------------------")
	print("|                                                  MESSAGE EDITOR                                                     |")
	print("-----------------------------------------------------------------------------------------------------------------------")
	print("|  start            -  Start the match. Only works as Host.                                                           |")
	print("|  exit             -  Leave the room                                                                                 |")
	print("|  close            -  Close this editor                                                                              |")
	print("|  invite           -  Invite a friend to the room                                                                    |")
	print("-----------------------------------------------------------------------------------------------------------------------")
	print("|  Type something and press enter to send a message to the chat!                                                      |")
	print("-----------------------------------------------------------------------------------------------------------------------")
	print("")
	print("")
	print("")
	os.system('stty echo')
	userInput = input("~Editor: ")
	Config.openEditor = False
	return userInput

def render_online_chat(chatHistory, playersInRoom):
	os.system('clear')
	print_banner()
	print_live_chat_help()
	print("-----------------------------------------------------------------------------------------------------------------------")
	print("|                                                     LIVE CHAT                                                       |")
	print("-----------------------------------------------------------------------------------------------------------------------")
	print("|                                                                                                                     |")
	print("  Players currently in the room (top one is the host): ")
	for p in playersInRoom:
		print("  " + p)
	print("|                                                                                                                     |")
	print("|                                                                                                                     |")
	for m in chatHistory:
		print("  " + m)
	print("|                                                                                                                     |")
	print("-----------------------------------------------------------------------------------------------------------------------\n")
	os.system('stty -echo')
