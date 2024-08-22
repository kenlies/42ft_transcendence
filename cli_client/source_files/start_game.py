import os
import time
import json
import signal
import asyncio
import websockets
from .config import Config, init_ssl_context
from .game_loop import pong, print_game_over
from .utils_and_signals import handle_sigstop, receive_no_wait
from .print_banners_docs import print_banner, print_available_commands
from .online_lobby import render_online_chat, online_editor, send_invite
from .local_lobby import render_local_notifications_board, local_editor


##############################################################################################################
############################################ GAME SETUP ######################################################
##############################################################################################################

def choose_mode():
	os.system('clear')
	print_banner()
	print("-----------------------------------------------------------------------------------------------------------------------")
	print("|                                                  CHOOSE GAME MODE                                                   |")
	print("-----------------------------------------------------------------------------------------------------------------------")
	print("|  1. Play online 1v1                                                                                                 |")
	print("|  2. Play local 1v1                                                                                                  |")
	print("|  3. Play online tournament                                                                                          |")
	print("|  4. Play local tournament                                                                                           |")
	print("-----------------------------------------------------------------------------------------------------------------------")
	print("")
	print("")
	try:
		while True:
			userInput = input("Enter the number of the mode you want to play: ")
			if userInput == '1':
				asyncio.get_event_loop().run_until_complete(start_1v1_game(is_local=False))
				break
			elif userInput == '2':
				asyncio.get_event_loop().run_until_complete(start_1v1_game(is_local=True))
				break
			elif userInput == '3':
				asyncio.get_event_loop().run_until_complete(start_tournament(is_local=False))
				break
			elif userInput == '4':
				asyncio.get_event_loop().run_until_complete(start_tournament(is_local=True))
				break
			print("Invalid command. Please try again.")
	except:
		print("Server disconnected. Please try again.")
		time.sleep(Config.wait_time)
	os.system('clear')
	os.system('stty echo')
	print_banner()
	print_available_commands()

def render_match_options_selection():
	print_banner()
	print("-----------------------------------------------------------------------------------------------------------------------")
	print("|                                                  GAME OPTIONS                                                       |")
	print("-----------------------------------------------------------------------------------------------------------------------")
	print("|                           Choose settings for the match or go with the default settings                             |")
	print("-----------------------------------------------------------------------------------------------------------------------")
	print("")
	print("")
	print("")

def ask_settings():
	while True:
		userInput = input("Would you like to set custom settings? (y/n): ")
		if (userInput == 'y' or userInput == 'Y' or userInput == 'yes' or userInput == 'Yes'):
			break
		elif (userInput == 'n' or userInput == 'N' or userInput == 'no' or userInput == 'No'):
			break
		else:
			print("Invalid command. Please try again.")
	if (userInput == 'y' or userInput == 'Y' or userInput == 'yes' or userInput == 'Yes'):
		while True:
			ballSpeed = input("Enter the speed of the ball (min: 0.001, max: 0.05): ")
			try:
				ballSpeed = float(ballSpeed)
			except:
				print("Invalid speed. Please try again.")
				continue
			if (ballSpeed < 0.001 or ballSpeed > 0.05):
				print("Invalid speed. Please try again.")
				continue
			else:
				break
		while True:
			paddleSpeed = input("Enter the speed of the paddles (min: 0.001, max: 0.05): ")
			try:
				paddleSpeed = float(paddleSpeed)
			except:
				print("Invalid speed. Please try again.")
				continue
			if (paddleSpeed < 0.001 or paddleSpeed > 0.05):
				print("Invalid speed. Please try again.")
				continue
			else:
				break
	else:
		ballSpeed = 0.02
		paddleSpeed = 0.03
	return ballSpeed, paddleSpeed


##############################################################################################################
############################################ START GAME ######################################################
##############################################################################################################

async def start_1v1_game(is_local=False):
    os.system('clear')
    print_banner()
    if is_local:
        player1 = input("Enter the name of the first player: ")
        player2 = input("Enter the name of the second player: ")
    print('Connecting to the server...')
    if is_local:
        urlWithQuery = Config.flowUrl + "/api/matchmaker?player1=" + player1 + "&player2=" + player2 + "&gameMode=local"
    else:
        urlWithQuery = Config.flowUrl + "/api/matchmaker?username=" + Config.username + "&gameMode=online"
    response = Config.session.get(urlWithQuery, verify=False)
    response.raise_for_status()
    url = response.json()["url"]
    ssl_context = init_ssl_context()
    async with websockets.connect(url, ssl=ssl_context) as ws:
        Config.currentWebSocket = ws
        if is_local:
            await local_room(ws, [player1, player2], is_tournament=False)
        else:
            await online_room(ws, is_tournament=False)
        await ws.close()
        Config.currentWebSocket = None

async def start_tournament(is_local=False):
    os.system('clear')
    print_banner()
    if is_local:
        player1 = input("Enter the name of the first player: ")
        player2 = input("Enter the name of the second player: ")
        player3 = input("Enter the name of the third player: ")
        player4 = input("Enter the name of the fourth player: ")
    print('Connecting to the server...')
    if is_local:
        urlWithQuery = Config.flowUrl + "/api/matchmaker?player1=" + player1 + "&player2=" + player2 + "&player3=" + player3 + "&player4=" + player4 + "&gameMode=localTournament"
    else:
        urlWithQuery = Config.flowUrl + "/api/matchmaker?username=" + Config.username + "&gameMode=onlineTournament"
    response = Config.session.get(urlWithQuery, verify=False)
    response.raise_for_status()
    url = response.json()["url"]
    ssl_context = init_ssl_context()
    async with websockets.connect(url, ssl=ssl_context) as ws:
        Config.currentWebSocket = ws
        if is_local:
            await local_room(ws, [player1, player2, player3, player4], is_tournament=True)
        else:
             await online_room(ws, is_tournament=True)
        await ws.close()
        Config.currentWebSocket = None


##############################################################################################################
############################################ LOCAL ROOM ######################################################
##############################################################################################################

async def local_room(ws, players, is_tournament=False):
	signal.signal(signal.SIGTSTP, handle_sigstop)
	Config.openEditor = False
	notifications = ['Players']
	for i, player in enumerate(players):
		notifications.append(f"Player{i+1}: {player}")
	notifications.append('')
	render_local_notifications_board(notifications)

	while True:
		if Config.openEditor:
			userInput = local_editor()
			if (userInput == 'start'):
				os.system('clear')
				render_match_options_selection()
				ballSpeed, paddleSpeed = ask_settings()
				message_type = "start_tournament" if is_tournament else "start_match"
				await ws.send(json.dumps({"type": message_type, "ballSpeed": ballSpeed, "paddleSpeed": paddleSpeed}))
			elif (userInput == 'exit'):
				break
			elif (userInput == 'close'):
				os.system('clear')
				render_local_notifications_board(notifications)
		
		message = await receive_no_wait(ws)
		if message is not None:
			message = json.loads(message)
			if message["identity"] == "start_match":
				os.system('clear')
				os.system('stty echo')
				winner = await pong(ws, message, is_local=True)
				if is_tournament:
					notifications.append("Winner is: " + winner)
					render_local_notifications_board(notifications)
				else:
					print_game_over(winner)
				Config.openEditor = False
				if not is_tournament:
					break

			elif message["identity"] == "message":
				notifications.append(message["sender"] + ": " + message["message"])
				render_local_notifications_board(notifications)
			elif message["identity"] == "error":
				notifications.append("Error: " + message["message"])
				render_local_notifications_board(notifications)

			elif message["identity"] == "tournament_over" and is_tournament:
				os.system('clear')
				os.system('stty echo')
				print_banner()
				print("The tournament is over. The winner is: " + message["winner"])
				print("\n\n")
				input("Press enter to return home.")
				break


##############################################################################################################
############################################ ONLINE ROOM #####################################################
##############################################################################################################

async def online_room(ws, is_tournament=False):
	signal.signal(signal.SIGTSTP, handle_sigstop)
	await ws.send(json.dumps({"type": "room_data_request"}))
	chatHistory = []
	playersInRoom = []
	Config.openEditor = False
	render_online_chat(chatHistory, playersInRoom)
	response = Config.session.get(Config.flowUrl + "/api/user?username=" + Config.username, headers={"Content-Type": "application/json", "X-CSRFToken": Config.session.cookies["csrftoken"], "session-id": Config.session.cookies["sessionid"], "Referer": Config.flowReferer}, verify=False)
	response.raise_for_status()
	blockedList = response.json()["blocked"]

	while True:
		if Config.openEditor:
			userInput = online_editor()
			if (userInput == 'start'):
				os.system('clear')
				render_match_options_selection()
				ballSpeed, paddleSpeed = ask_settings()
				message_type = "start_tournament" if is_tournament else "start_match"
				await ws.send(json.dumps({"type": message_type, "ballSpeed": ballSpeed, "paddleSpeed": paddleSpeed}))
			elif (userInput == 'exit'):
				break
			elif (userInput == 'close'):
				render_online_chat(chatHistory, playersInRoom)
			elif (userInput == 'invite'):
				await send_invite(ws)
				render_online_chat(chatHistory, playersInRoom)
			else:
				await ws.send(json.dumps({"type": "message", "message": userInput, "sender": Config.username}))

		message = await receive_no_wait(ws)
		if message is not None:
			message = json.loads(message)
			if message["identity"] == "message":
				sender = "You" if message["sender"] == Config.username else message["sender"]
				if sender not in blockedList:
					chatHistory.append(f"{sender}: {message['message']}")
					render_online_chat(chatHistory, playersInRoom)

			elif message["identity"] == "start_match":
				os.system('clear')
				os.system('stty echo')
				if is_tournament:
					winner = await pong(ws, message, is_local=False)
					if winner == None:
						os.system('clear')
						print_banner()
						print("Host has left the room. The tournament is interrupted.")
						input("Press enter to return home.")
						break
					chatHistory.append("Winner is: " + winner)
					render_online_chat(chatHistory, playersInRoom)
				else:
					print_game_over(await pong(ws, message, is_local=False))
				Config.openEditor = False
				if not is_tournament:
					break

			elif message["identity"] == "error":
				chatHistory.append("Error: " + message["message"])
				render_online_chat(chatHistory, playersInRoom)
			elif message["identity"] == "room_data":
				playersInRoom = []
				playersInRoom.append(message["player1"])
				playersInRoom.append(message["player2"])
				if is_tournament:
					playersInRoom.append(message["player3"])
					playersInRoom.append(message["player4"])
				render_online_chat(chatHistory, playersInRoom)
			elif message['identity'] == 'room_closed':
				break

			elif message["identity"] == "tournament_over" and is_tournament:
				os.system('clear')
				os.system('stty echo')
				print_banner()
				print("The tournament is over. The winner is: " + message["winner"])
				print("\n\n")
				input("Press enter to return home.")
				break
