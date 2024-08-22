import os
import time
import json
import queue
from pynput import keyboard
from typing import NamedTuple
from .config import Config
from .utils_and_signals import receive_no_wait
from .print_banners_docs import print_banner

def print_game_over(winner):
	os.system('clear')
	print_banner()
	print("-----------------------------------------------------------------------------------------------------------------------")
	print("|                                                      GAME OVER                                                      |")
	print("-----------------------------------------------------------------------------------------------------------------------")
	print("|                                                                                                                     |")
	print("  The winner is: " + winner)
	print("|                                                                                                                     |")
	print("-----------------------------------------------------------------------------------------------------------------------\n")
	print("Press enter to return home.")
	os.system('stty echo')
	input()
	os.system('stty -echo')

async def send_to_server(websocket, value):
	await websocket.send(json.dumps({"type": "paddle_position", "value": value}))

def on_press_online(key):
	try:
		if (Config.myRole == 1):
			oldPosition = Config.game_state.player1_paddle_y
		elif (Config.myRole == 2):
			oldPosition = Config.game_state.player2_paddle_y
		else:
			return
		if hasattr(key, 'char'):
			if key.char == 'w':
				Config.inputQueue.put(oldPosition - Config.paddleSpeed)
			elif key.char == 's':
				Config.inputQueue.put(oldPosition + Config.paddleSpeed)
		elif key == keyboard.Key.up:
			Config.inputQueue.put(oldPosition - Config.paddleSpeed)
		elif key == keyboard.Key.down:
			Config.inputQueue.put(oldPosition + Config.paddleSpeed)
	except:
		pass

class GameState(NamedTuple):
	court_height: int
	court_width: int
	player1_paddle_y: float
	player2_paddle_y: float
	player1_paddle_x: int
	player2_paddle_x: int
	ball_x: float
	ball_y: float
	goals_player1: int
	goals_player2: int
	paddle_height: int
	ball_delta_x: float
	ball_delta_y: float

def scale_to_terminal(value: float, max_value: int) -> float:
	return value * (max_value - 1)

def print_game(game_state: GameState):
	os.system('clear')
	scaled_p1_paddle_y = int(scale_to_terminal(game_state.player1_paddle_y, game_state.court_height))
	scaled_p2_paddle_y = int(scale_to_terminal(game_state.player2_paddle_y, game_state.court_height))
	court = [[' ' for _ in range(game_state.court_width)] for _ in range(game_state.court_height)]
	for x in range(game_state.court_width):
		court[0][x] = '━'
		court[-1][x] = '━'
	for y in range(scaled_p1_paddle_y + 1, scaled_p1_paddle_y + game_state.paddle_height):
		if 0 <= y <= game_state.court_height:
			court[y][game_state.player1_paddle_x] = '█'
	for y in range(scaled_p2_paddle_y + 1, scaled_p2_paddle_y + game_state.paddle_height):
		if 0 <= y <= game_state.court_height:
			court[y][game_state.player2_paddle_x] = '█'
	ball_x_int, ball_y_int = int(round(game_state.ball_x)), int(round(game_state.ball_y))
	if 0 <= ball_y_int < game_state.court_height and 0 <= ball_x_int < game_state.court_width:
		court[ball_y_int][ball_x_int] = '●'
	for row in court:
		print(''.join(row))
	current_time = time.strftime("%H:%M:%S", time.localtime())
	print(f"\nPlayer 1: {game_state.goals_player1} | Player 2: {game_state.goals_player2} | Time: {current_time}")

def initialize_game(websocket, matchMetaData):
	Config.currentWebSocket = websocket
	Config.inputQueue = queue.Queue()

	if (matchMetaData['player1_username'] == Config.username):
		Config.myRole = 1
	elif (matchMetaData['player2_username'] == Config.username):
		Config.myRole = 2

	court_height = 60
	court_width = 180

	paddle_height = int(matchMetaData['paddleHeight'] * court_height)
	Config.paddleSpeed = float(matchMetaData['paddleSpeed'])

	Config.game_state = GameState(
		court_height=court_height,
		court_width=court_width,
		player1_paddle_y=matchMetaData['player1Paddle_y_top'],
		player2_paddle_y=matchMetaData['player2Paddle_y_top'],
		player1_paddle_x=int(scale_to_terminal(matchMetaData['player1Paddle_x'], court_width)),
		player2_paddle_x=int(scale_to_terminal(matchMetaData['player2Paddle_x'], court_width)),
		ball_x=scale_to_terminal(matchMetaData['ball_x'], court_width),
		ball_y=scale_to_terminal(matchMetaData['ball_y'], court_height),
		goals_player1=matchMetaData['goalsPlayer1'],
		goals_player2=matchMetaData['goalsPlayer2'],
		paddle_height=paddle_height,
		ball_delta_x=matchMetaData['ballDeltaX'] * court_width,
		ball_delta_y=matchMetaData['ballDeltaY'] * court_height
	)
	return court_width, court_height

async def pong(websocket, matchMetaData):
	try:
		court_width, court_height = initialize_game(websocket, matchMetaData)

		listener = keyboard.Listener(on_press=on_press_online)
		listener.start()

		print_game(Config.game_state)
		last_draw_time = time.time()

		while True: 
			latest_data = None
			response = "empty"
			while True:
				if response is None:
					break
				if latest_data is not None and latest_data["identity"] != "game_update":
					break
				response = await receive_no_wait(websocket)
				if response is not None:
					latest_data = json.loads(response)
			if latest_data is not None:
				if latest_data["identity"] == "game_update":
					Config.game_state = Config.game_state._replace(
						player1_paddle_y=latest_data["positions"]["player1Paddle_y_top"],
						player2_paddle_y=latest_data["positions"]["player2Paddle_y_top"],
						ball_x=scale_to_terminal(latest_data["positions"]["ball_x"], court_width),
						ball_y=scale_to_terminal(latest_data["positions"]["ball_y"], court_height),
						goals_player1=latest_data["positions"]["goalsPlayer1"],
						goals_player2=latest_data["positions"]["goalsPlayer2"],
						ball_delta_x=latest_data["positions"]["ballDeltaX"] * court_width,
						ball_delta_y=latest_data["positions"]["ballDeltaY"] * court_height
					)
				elif latest_data["identity"] == "game_over":
					listener.stop()
					return latest_data["winner"]
				elif latest_data["identity"] == "room_closed":
					listener.stop()
					return None
			while not Config.inputQueue.empty():
				value = Config.inputQueue.get()
				await send_to_server(websocket, value)

			current_time = time.time()
			if current_time - last_draw_time >= 0.1:
				last_draw_time = current_time
				print_game(Config.game_state)
	except:
		pass
	finally:
		listener.stop()
