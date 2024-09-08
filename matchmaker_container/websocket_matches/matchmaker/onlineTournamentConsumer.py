import os
import json
import time
import random
import asyncio
import requests
from queue import Queue
from urllib.parse import parse_qsl
from .models import OnlineTournament
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async
from matchmaker.update import update_players, update_ball
from channels.generic.websocket import AsyncWebsocketConsumer
from matchmaker.constants import PADDLE_HEIGHT, COURT_HEIGHT, COURT_WIDTH

channel_layer = get_channel_layer()

class onlineTournamentConsumer(AsyncWebsocketConsumer):

	async def init_match_meta_data(self, ballSpeed, paddleSpeed):
		self.courtHeight = COURT_HEIGHT
		self.courtWidth = COURT_WIDTH
		self.paddleHeight = PADDLE_HEIGHT

		self.ballSpeed = float(ballSpeed) / 10
		self.paddleSpeed = float(paddleSpeed)

		self.ball_y = COURT_HEIGHT / 2
		self.ball_x = COURT_WIDTH / 2
		self.ballDeltaY = 0.0
		self.ballDeltaX = self.ballSpeed

		self.player1Paddle_y_top = (COURT_HEIGHT - self.paddleHeight) / 2
		self.player1Paddle_x = 0.0

		self.player2Paddle_y_top = self.player1Paddle_y_top
		self.player2Paddle_x = COURT_WIDTH

		self.goalsPlayer1 = 0
		self.goalsPlayer2 = 0

		self.player1_update_queue = Queue()
		self.player2_update_queue = Queue()


	async def reset_match_data(self):
		self.ball_y = COURT_HEIGHT / 2
		self.ball_x = COURT_WIDTH / 2
		self.ballDeltaY = 0.0
		self.ballDeltaX = self.ballSpeed

		self.player1Paddle_y_top = (COURT_HEIGHT - self.paddleHeight) / 2
		self.player1Paddle_x = 0.0

		self.player2Paddle_y_top = self.player1Paddle_y_top
		self.player2Paddle_x = COURT_WIDTH

		self.goalsPlayer1 = 0
		self.goalsPlayer2 = 0

		self.player1_update_queue = Queue()
		self.player2_update_queue = Queue()

		self.confirmedPlayers = []
		self.allConfirmed = False

	def get_username_from_role(self, role):
		if (role == 1):
			return self.player1Username
		elif (role == 2):
			return self.player2Username
		elif (role == 3):
			return self.player3Username
		elif (role == 4):
			return self.player4Username
		else:
			return "Unknown"

	###################################################################
	########################### CLIENT LOGIC ##########################
	###################################################################

	################### CONNECT AND DISCONNECT WEBSOCKETS ##################
	async def connect(self):
		try:
			self.room_name = self.scope['url_route']['kwargs']['game_room']
			thetournament = await database_sync_to_async(OnlineTournament.objects.get)(roomId=self.room_name)
			self.room_group_name = 'match_%s' % self.room_name
			await self.channel_layer.group_add(
				self.room_group_name,
				self.channel_name
			)
			await self.accept()
			self.username = dict(parse_qsl(self.scope['query_string'].decode('utf-8'))).get('username')
			match self.username:
				case thetournament.player1:
					self.role = 1
				case thetournament.player2:
					self.role = 2
				case thetournament.player3:
					self.role = 3
				case thetournament.player4:
					self.role = 4
			thetournament.playerCount += 1
			if (self.role == 4): #handle last player joining through invite
				thetournament.ready = True
			await database_sync_to_async(thetournament.save)()
			self.inGame = False
			self.is_disconnecting = False
			if self.role == 1:
				self.loopTaskActive = False
				self.connectedPlayers = []
				self.confirmedPlayers = []
				self.allConfirmed = False
				self.gameOnGoing = False
				self.currentPLayer1 = 0
				self.currentPLayer2 = 0
				self.speed = 25
			elif self.role > 4: #handle more than 4 players through invite
				self.close()
			await self.channel_layer.group_send(
				self.room_group_name,
				{
					'type': 'player_connected',
					'role': self.role
				}
			)
		except thetournament.DoesNotExist:
			print("Match object not found")
			return


	async def disconnect(self, close_code):
		self.is_disconnecting = True
		try:
			thetournament = await database_sync_to_async(OnlineTournament.objects.get)(roomId=self.room_name)
			matchObjectExists = True
		except:
			matchObjectExists = False
		try:
			if matchObjectExists and self.role == 1:
				await self.channel_layer.group_send(
					self.room_group_name,
					{
						'type': 'room_closed',
						'username': self.username
					}
				)
				await database_sync_to_async(thetournament.delete)()
				if (self.loopTaskActive):
					self.loopTaskActive = False
					self.game_loop_task.cancel()
			else:
				await self.channel_layer.group_send(
					self.room_group_name,
					{
						'type': 'player_disconnected',
						'username': self.username,
						'role': self.role
					}
				)
				if thetournament.hasCommenced == False:
					if self.role < 3:
						thetournament.player2 = thetournament.player3
						thetournament.player3 = ''
					if self.role < 4:
						thetournament.player3 = thetournament.player4
						thetournament.player4 = ''
					if self.role == 4:
						thetournament.player4 = ''
					thetournament.playerCount -= 1
					thetournament.ready = False
					await database_sync_to_async(thetournament.save)()
					await self.channel_layer.group_send(
						self.room_group_name,
						{
							'type': 'room_data',
							'player1': thetournament.player1,
							'player2': thetournament.player2,
							'player3': thetournament.player3,
							'player4': thetournament.player4
						}
					)
			await self.channel_layer.group_discard(
				self.room_group_name,
				self.channel_name
			)
			self.close()
		except:
			self.close()

	############ GAME LOGIC ############

	async def send_start_match(self, player1, player2):
		await self.channel_layer.group_send(
			self.room_group_name,
			{
				'type': 'start_match',
				'paddleSpeed': self.paddleSpeed,
				'paddleHeight': self.paddleHeight,
				'courtHeight': self.courtHeight,
				'courtWidth': self.courtWidth,
				'player1Paddle_y_top': self.player1Paddle_y_top,
				'player2Paddle_y_top': self.player2Paddle_y_top,
				'player1Paddle_x': self.player1Paddle_x,
				'player2Paddle_x': self.player2Paddle_x,
				'ball_y': self.ball_y,
				'ball_x': self.ball_x,
				'ballDeltaY' : self.ballDeltaY,
				'ballDeltaX' : self.ballDeltaX,
				"ballSpeed": self.ballSpeed,
				'goalsPlayer1': self.goalsPlayer1,
				'goalsPlayer2': self.goalsPlayer2,
				'player1_username': player1,
				'player2_username': player2
			}
		)

	async def wait_for_confirmed(self, player1, player2):
		start_time = time.time()
		while (self.allConfirmed == False):
			await self.send_start_match(self.get_username_from_role(player1), self.get_username_from_role(player2))
			await asyncio.sleep(2)
			if (time.time() - start_time > 15):
				for player in self.connectedPlayers:
					if player not in self.confirmedPlayers:
						await self.channel_layer.group_send(
							self.room_group_name,
							{
								'type': 'live_message',
								'message': 'Player ' + self.get_username_from_role(player) + ' has been disconnected due to a network error.',
								'sender': 'System'
							}
						)
						await self.channel_layer.group_send(
							self.room_group_name,
							{
								'type': 'time_out_disconnect',
								'role': player
							}
						)
				return

	async def single_match(self, player1, player2):
		self.gameOnGoing = True
		self.abort = False
		self.currentPLayer1 = player1
		self.currentPLayer2 = player2
		await self.wait_for_confirmed(player1, player2)
		while (self.goalsPlayer1 < 5 and self.goalsPlayer2 < 5 and not self.abort):
			await update_players(self)
			await update_ball(self)
			positions = {
				"ball_y": self.ball_y,
				"ball_x": self.ball_x,
				"ballDeltaY" : self.ballDeltaY,
				"ballDeltaX" : self.ballDeltaX,
				"player1Paddle_y_top": self.player1Paddle_y_top,
				"player2Paddle_y_top": self.player2Paddle_y_top,
				"goalsPlayer1": self.goalsPlayer1,
				"goalsPlayer2": self.goalsPlayer2
			}
			await self.channel_layer.group_send(
				self.room_group_name,
				{
					'type': 'game_update',
					'positions': positions
				}
			)
			await asyncio.sleep(0.01)
		if (self.goalsPlayer1 >= 5 or self.goalsPlayer2 >= 5 or self.abort):
			if self.abort:
				winner = self.winner_through_disconnect
			else:
				winner = player1 if self.goalsPlayer1 >= 5 else player2
			await self.channel_layer.group_send(
				self.room_group_name,
				{
					'type': 'game_over',
					'winner': self.get_username_from_role(winner)
				}
			)
		self.gameOnGoing = False
		if self.abort:
			return self.winner_through_disconnect
		return player1 if self.goalsPlayer1 >= 5 else player2

	async def record_match(self, winner, loser):
		secret = os.environ.get("MATCHMAKER_SECRET")
		data = {
			'secret': secret,
			'matchId': self.room_name,
			'matchWinner': self.get_username_from_role(winner),
			'matchLoser': self.get_username_from_role(loser),
			'matchWinnerScore': self.goalsPlayer1 if winner == self.currentPLayer1 else self.goalsPlayer2,
			'matchLoserScore': self.goalsPlayer1 if loser == self.currentPLayer1 else self.goalsPlayer2
		}
		try:
			requests.post("http://flow:8000/api/match", data=json.dumps(data))
		except:
			print("Error posting match data to flow api")

	async def tournament(self):
		await asyncio.sleep(0.01)
		shuffled = [1, 2, 3, 4]
		random.shuffle(shuffled)
		self.firstLevelMatch1 = [shuffled[0], shuffled[1]]
		self.firstLevelMatch2 = [shuffled[2], shuffled[3]]
		theTournament = await database_sync_to_async(OnlineTournament.objects.get)(roomId=self.room_name)
		self.player1Username = theTournament.player1
		self.player2Username = theTournament.player2
		self.player3Username = theTournament.player3
		self.player4Username = theTournament.player4
		await self.channel_layer.group_send(
			self.room_group_name,
			{
				'type': 'live_message',
				'message': 'The first match is between ' + self.get_username_from_role(self.firstLevelMatch1[0]) + ' and ' + self.get_username_from_role(self.firstLevelMatch1[1]),
				'sender': 'System'
			}
		)
		await asyncio.sleep(5)
		if self.firstLevelMatch1[0] in self.connectedPlayers and self.firstLevelMatch1[1] in self.connectedPlayers:
			self.match1Winner = await self.single_match(self.firstLevelMatch1[0], self.firstLevelMatch1[1])
			await self.record_match(self.match1Winner, self.firstLevelMatch1[0] if self.match1Winner == self.firstLevelMatch1[1] else self.firstLevelMatch1[1])
			await self.reset_match_data()
		elif self.firstLevelMatch1[0] in self.connectedPlayers:
			self.match1Winner = self.firstLevelMatch1[0]
		else:
			self.match1Winner = self.firstLevelMatch1[1]
		await asyncio.sleep(2)
		await self.channel_layer.group_send(
			self.room_group_name,
			{
				'type': 'live_message',
				'message': 'The second match is between ' + self.get_username_from_role(self.firstLevelMatch2[0]) + ' and ' + self.get_username_from_role(self.firstLevelMatch2[1]),
				'sender': 'System'
			}
		)
		await asyncio.sleep(5)
		if self.firstLevelMatch2[0] in self.connectedPlayers and self.firstLevelMatch2[1] in self.connectedPlayers:
			self.match2Winner = await self.single_match(self.firstLevelMatch2[0], self.firstLevelMatch2[1])
			await self.record_match(self.match2Winner, self.firstLevelMatch2[0] if self.match2Winner == self.firstLevelMatch2[1] else self.firstLevelMatch2[1])
			await self.reset_match_data()
		elif self.firstLevelMatch2[0] in self.connectedPlayers:
			self.match2Winner = self.firstLevelMatch2[0]
		else:
			self.match2Winner = self.firstLevelMatch2[1]
		await asyncio.sleep(5)
		await self.channel_layer.group_send(
			self.room_group_name,
			{
				'type': 'live_message',
				'message': 'The final match is between ' + self.get_username_from_role(self.match1Winner) + ' and ' + self.get_username_from_role(self.match2Winner),
				'sender': 'System'
			}
		)
		await asyncio.sleep(5)
		if self.match1Winner in self.connectedPlayers and self.match2Winner in self.connectedPlayers:
			self.tournamentWinner = await self.single_match(self.match1Winner, self.match2Winner)
			await self.record_match(self.tournamentWinner, self.match1Winner if self.tournamentWinner == self.match2Winner else self.match2Winner)
			await self.reset_match_data()
		elif self.match1Winner in self.connectedPlayers:
			self.tournamentWinner = self.match1Winner
		else:
			self.tournamentWinner = self.match2Winner
		for _ in range(2):
			await self.channel_layer.group_send(
				self.room_group_name,
				{
					'type': 'tournament_over',
					'winner': self.get_username_from_role(self.tournamentWinner)
				}
			)
			await asyncio.sleep(2)

	################### RECEIVE DATA ON WEBSOCKETS ##################
	async def receive(self, text_data):
		data = json.loads(text_data)
		if ('type' in data):
			if (data['type'] == 'paddle_position' and 'value' in data):
				await self.channel_layer.group_send(
						self.room_group_name,
						{
							'type': 'paddle_position',
							'position': data["value"],
							'role': self.role
						}
					)
			elif (data['type'] == 'received_start_match'):
				await self.channel_layer.group_send(
					self.room_group_name,
					{
						'type': 'received_start_match',
						'role': self.role
					}
				)
			elif (data['type'] == 'room_data_request'):
				theTournament = await database_sync_to_async(OnlineTournament.objects.get)(roomId=self.room_name)
				await self.channel_layer.group_send(
					self.room_group_name,
					{
						'type': 'room_data',
						'player1': theTournament.player1,
						'player2': theTournament.player2,
						'player3': theTournament.player3,
						'player4': theTournament.player4
					}
				)
			elif (data['type'] == 'message' and 'message' in data and 'sender' in data):
				await self.channel_layer.group_send(
					self.room_group_name,
					{
						'type': 'live_message',
						'message': data['message'],
						'sender': data['sender']
					}
				)
			elif (data['type'] == 'start_tournament' and 'ballSpeed' in data and 'paddleSpeed' in data and not self.loopTaskActive):
				if (self.role != 1):
					await self.send(json.dumps({
						'identity': 'error',
						'message': 'Cannot start the tournament. You are not the host.'
					}))
				if (self.role == 1):
					if (type(data['ballSpeed']) != float or type(data['paddleSpeed']) != float):
						await self.send(json.dumps({
							'identity': 'error',
							'message': 'Invalid data format. Data must be floats. Allowed values are ballSpeed: 0.001-0.05, paddleSpeed: 0.001-0.05'
						}))
					elif (data['ballSpeed'] < 0.001 or data['paddleSpeed'] < 0.001):
						await self.send(json.dumps({
							'identity': 'error',
							'message': 'Invalid data format. Negative values not allowed. Allowed values are ballSpeed: 0.001-0.05, paddleSpeed: 0.001-0.05'
						}))
					elif (data['ballSpeed'] > 0.05 or data['paddleSpeed'] > 0.05):
						await self.send(json.dumps({
							'identity': 'error',
							'message': 'Invalid data format. Value too high. Allowed values are ballSpeed: 0.001-0.05, paddleSpeed: 0.001-0.05'
						}))
					else:
						print("Received start tournament")
						theTournament = await database_sync_to_async(OnlineTournament.objects.get)(roomId=self.room_name)
						if theTournament.ready:
							ballSpeed = data['ballSpeed']
							paddleSpeed = data['paddleSpeed']
							theTournament.hasCommenced = True
							await database_sync_to_async(theTournament.save)()
							await self.init_match_meta_data(ballSpeed, paddleSpeed)
							await self.channel_layer.group_send(
								self.room_group_name,
								{
									'type': 'live_message',
									'message': 'Tournament has started. Get ready!',
									'sender': 'System'
								}
							)
							self.loopTaskActive = True
							self.game_loop_task = asyncio.create_task(self.tournament())
						else:
							await self.send(json.dumps({
								'identity': 'error',
								'message': 'Not enough players to start the Tournament.'
							}))
			elif (data['type'] == 'invite' and 'receiver' in data):
				theTournament = await database_sync_to_async(OnlineTournament.objects.get)(roomId=self.room_name)
				if (self.role == 1 and theTournament.playerCount < 5):
					data = {
						'secret': os.environ.get("MATCHMAKER_SECRET"),
						'sender': theTournament.player1,
						'receiver': data['receiver'],
						'url': '/match/connect/onlineTournament/' + theTournament.roomId
					}
					response = requests.post("http://flow:8000/api/invite", data=json.dumps(data))
					if response.status_code != 201:
						print("Error sending invite to flow api")
						return
					if (theTournament.playerCount == 2):
						theTournament.player2 = data['receiver']
					elif (theTournament.playerCount == 3):
						theTournament.player3 = data['receiver']
					elif (theTournament.playerCount == 4):
						theTournament.player4 = data['receiver']
					else:
						return
					await database_sync_to_async(theTournament.save)()
					await self.channel_layer.group_send(
						self.room_group_name,
						{
							'type': 'live_message',
							'message': 'Invite has been sent to ' + data['receiver'],
							'sender': 'System'
						}
					)
				else:
					await self.send(json.dumps({
						'identity': 'error',
						'message': 'Cannot send invite.'
					}))
			elif (data['type'] == 'setting_change' and 'value' in data):
				if (self.role == 1):
					await self.channel_layer.group_send(
						self.room_group_name,
						{
							'type': 'setting_change',
							'value': data['value']
						}
					)
		else:
			await self.send(json.dumps({
				'identity': 'error',
				'message': 'Invalid data format'
			}))


	################### SEND DATA ON WEBSOCKETS ##################
	async def room_data(self, event):
		if not self.is_disconnecting:
			await self.send(json.dumps({
				'identity': 'room_data',
				'player1': event['player1'],
				'player2': event['player2'],
				'player3': event['player3'],
				'player4': event['player4']
			}))

	async def setting_change(self, event):
		if self.role == 1:
			self.speed = event['value']
		if not self.is_disconnecting:
			await self.send(json.dumps({
				'identity': 'setting_change',
				'value': event['value']
			}))

	async def room_closed(self, event):
		if not self.is_disconnecting:
			await self.send(json.dumps({
				'identity': 'room_closed',
				'username': event['username']
			}))

	async def live_message(self, event):
		if not self.is_disconnecting:
			await self.send(json.dumps({
				'identity': 'message',
				'message': event['message'],
				'sender': event['sender']
			}))

	async def paddle_position(self, event):
		if (self.role == 1 and self.loopTaskActive and self.gameOnGoing):
			if 'position' in event and 'role' in event:
				if (event['role'] == self.currentPLayer1):
					self.player1_update_queue.put(event['position'])
				elif (event['role'] == self.currentPLayer2):
					self.player2_update_queue.put(event['position'])

	async def game_update(self, event):
		positions = event['positions']
		if not self.is_disconnecting:
			await self.send(json.dumps({
				'identity': 'game_update',
				'positions': positions
			}))

	async def game_over(self, event):
		if not self.is_disconnecting:
			await self.send(json.dumps({
				'identity': 'game_over',
				'winner': event['winner']
			}))

	async def start_match(self, event):
		if not self.is_disconnecting:
			await self.send(json.dumps({
				'identity': 'start_match',
				'role': self.role,
				'paddleSpeed': event['paddleSpeed'],
				'paddleHeight': event['paddleHeight'],
				'courtHeight': event['courtHeight'],
				'courtWidth': event['courtWidth'],
				'player1Paddle_y_top': event['player1Paddle_y_top'],
				'player2Paddle_y_top': event['player2Paddle_y_top'],
				'player1Paddle_x': event['player1Paddle_x'],
				'player2Paddle_x': event['player2Paddle_x'],
				'ball_x': event['ball_x'],
				'ball_y': event['ball_y'],
				'ballDeltaY': event['ballDeltaY'],
				'ballDeltaX': event['ballDeltaX'],
				'ballSpeed': event['ballSpeed'],
				'goalsPlayer1': event['goalsPlayer1'],
				'goalsPlayer2': event['goalsPlayer2'],
				'player1_username': event['player1_username'],
				'player2_username': event['player2_username']
			}))

	async def player_disconnected(self, event):
		if not self.is_disconnecting:
			await self.send(json.dumps({
				'identity': 'player_disconnected',
				'username': event['username']
			}))
		try:
			theTournament = await database_sync_to_async(OnlineTournament.objects.get)(roomId=self.room_name)
			if self.role == 1:
				if theTournament.hasCommenced == False:
					self.connectedPlayers.pop()
				else:
					if event['role'] in self.connectedPlayers:
						self.connectedPlayers.remove(event['role'])
					if self.gameOnGoing and (event['role'] == self.currentPLayer1 or event['role'] == self.currentPLayer2):
						self.abort = True
						self.winner_through_disconnect = self.currentPLayer1 if self.currentPLayer1 != event['role'] else self.currentPLayer2
			elif theTournament.hasCommenced == False and self.role > event['role']:
				self.role -= 1
		except:
			pass

	async def player_connected(self, event):
		if self.role == 1:
			self.connectedPlayers.append(event['role'])
			await self.channel_layer.group_send(
				self.room_group_name,
				{
					'type': 'setting_change',
					'value': self.speed
				}
			)

	async def tournament_over(self, event):
		if not self.is_disconnecting:
			await self.send(json.dumps({
				'identity': 'tournament_over',
				'winner': event['winner']
			}))

	async def received_start_match(self, event):
		if self.role == 1:
			self.confirmedPlayers.append(event['role'])
			for player in self.connectedPlayers:
				if player not in self.confirmedPlayers:
					return
			self.allConfirmed = True

	async def time_out_disconnect(self, event):
		if self.role == event['role']:
			self.is_disconnecting = True
			await self.close()
