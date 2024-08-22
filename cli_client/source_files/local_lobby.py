import os
from .config import Config
from .print_banners_docs import print_banner, print_notifications_board_help

def local_editor():
	while True:
		os.system('clear')
		print_banner()
		print("-----------------------------------------------------------------------------------------------------------------------")
		print("|                                                  MESSAGE EDITOR                                                     |")
		print("-----------------------------------------------------------------------------------------------------------------------")
		print("|  start            -  Start the match. Only works as Host.                                                           |")
		print("|  exit             -  Leave the room                                                                                 |")
		print("|  close            -  Close this editor                                                                              |")
		print("-----------------------------------------------------------------------------------------------------------------------")
		print("")
		print("")
		print("")
		os.system('stty echo')
		userInput = input("~Editor: ")
		if (userInput == 'start' or userInput == 'exit' or userInput == 'close'):
			break
		else:
			print("Invalid command. Please try again.")
	Config.openEditor = False
	return userInput

def render_local_notifications_board(notifications):
	os.system('clear')
	print_banner()
	print_notifications_board_help()
	print("-----------------------------------------------------------------------------------------------------------------------")
	print("|                                                  NOTIFICATIONS BOARD                                                |")
	print("-----------------------------------------------------------------------------------------------------------------------")
	print("|                                                                                                                     |")
	for n in notifications:
		print("  " + n)
	print("|                                                                                                                     |")
	print("-----------------------------------------------------------------------------------------------------------------------\n")
	os.system('stty -echo')
