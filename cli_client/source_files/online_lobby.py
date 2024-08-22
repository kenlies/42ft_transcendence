import os
from .config import Config
from .print_banners_docs import print_banner, print_live_chat_help

def online_editor():
	os.system('clear')
	print_banner()
	print("-----------------------------------------------------------------------------------------------------------------------")
	print("|                                                  MESSAGE EDITOR                                                     |")
	print("-----------------------------------------------------------------------------------------------------------------------")
	print("|  start            -  Start the match. Only works as Host.                                                           |")
	print("|  exit             -  Leave the room                                                                                 |")
	print("|  close            -  Close this editor                                                                              |")
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
