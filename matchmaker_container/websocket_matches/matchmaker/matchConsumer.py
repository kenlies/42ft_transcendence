from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from .models import OnlineMatch
from asgiref.sync import sync_to_async
from queue import Queue
import asyncio
import json
import random
import requests
import os

# Define constants
COURT_HEIGHT = 1.0
COURT_WIDTH = 1.0
PADDLE_HEIGHT = 0.1

channel_layer = get_channel_layer()

class MatchConsumer(AsyncWebsocketConsumer):


	###################################################################
	########################### HOST LOGIC ############################
	###################################################################
	#-Only the host instance uses these functions
	#-Note: The host instance is the first instance to connect to the room
	#-Note: The host instance is the only instance that can start the match and close the room
	#-Note: The client that connects first, will not be slowed down by the game loop. It runs in the background and operates independently of the client

	#### INITIATE MATCH FUNCTIONS ####
	async def init_match(self, ballSpeed, paddleSpeed):
		self.courtHeight = COURT_HEIGHT
		self.courtWidth = COURT_WIDTH
		self.paddleHeight = PADDLE_HEIGHT

		self.ballSpeed = float(ballSpeed)
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

	async def initiate_start_match(self): # this calls the start_match function below in all client instances
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
				'goalsPlayer2': self.goalsPlayer2
			}
		)


	############ GAME LOGIC ############
	#-Utilized by host instance
	#-Update player positions and ball position and echo to all clients
	async def update_players(self):
		if (self.role == 1):
			while not self.player1_update_queue.empty(): # check that the bottom and top dont go over court height
				temp = self.player1_update_queue.get()
				if (temp == 'up'):
					if (self.player1Paddle_y_top - self.paddleSpeed >= 0):
						self.player1Paddle_y_top -= self.paddleSpeed
				elif (temp == 'down'):
					if (self.player1Paddle_y_top + PADDLE_HEIGHT + self.paddleSpeed < self.courtHeight):
						self.player1Paddle_y_top += self.paddleSpeed
			while not self.player2_update_queue.empty():
				temp = self.player2_update_queue.get()
				if (temp == 'up'):
					if (self.player2Paddle_y_top - self.paddleSpeed >= 0):
						self.player2Paddle_y_top -= self.paddleSpeed
				elif (temp == 'down'):
					if (self.player2Paddle_y_top + PADDLE_HEIGHT + self.paddleSpeed <= self.courtHeight):
						self.player2Paddle_y_top += self.paddleSpeed

	async def update_ball(self):
		self.ball_x += self.ballDeltaX
		self.ball_y += self.ballDeltaY
		if (self.ball_y <= 0):
			self.ballDeltaY = -self.ballDeltaY
			self.ball_y = 0
		elif (self.ball_y >= 1):
			self.ballDeltaY = -self.ballDeltaY
			self.ball_y = 1
		if (self.ball_x <= 0 and self.ball_x != self.player1Paddle_x and (self.ball_y < self.player1Paddle_y_top or self.ball_y > self.player1Paddle_y_top + PADDLE_HEIGHT)):
			self.goalsPlayer2 += 1
			self.ball_x = COURT_WIDTH / 2
			self.ball_y = COURT_HEIGHT / 2
			self.ballDeltaX = -self.ballSpeed
			self.ballDeltaY = 0.0
		elif (self.ball_x >= 1 and self.ball_x != self.player2Paddle_x and (self.ball_y < self.player2Paddle_y_top or self.ball_y > self.player2Paddle_y_top + PADDLE_HEIGHT)):
			self.goalsPlayer1 += 1
			self.ball_x = COURT_WIDTH / 2
			self.ball_y = COURT_HEIGHT / 2
			self.ballDeltaX = self.ballSpeed
			self.ballDeltaY = 0.0
		randomFactor = random.uniform(-self.ballSpeed, self.ballSpeed)
		if (self.ball_x <= self.player1Paddle_x and self.ball_y >= self.player1Paddle_y_top and self.ball_y <= self.player1Paddle_y_top + PADDLE_HEIGHT):
			self.ballDeltaX = -self.ballDeltaX
			self.ballDeltaY = randomFactor
		elif (self.ball_x >= self.player2Paddle_x and self.ball_y >= self.player2Paddle_y_top and self.ball_y <= self.player2Paddle_y_top + PADDLE_HEIGHT):
			self.ballDeltaX = -self.ballDeltaX
			self.ballDeltaY = randomFactor

	async def pong(self):
		while (self.goalsPlayer1 < 5 and self.goalsPlayer2 < 5):
			await self.update_players()
			await self.update_ball()
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
			await asyncio.sleep(0.1)
		if (self.goalsPlayer1 >= 5 or self.goalsPlayer2 >= 5):
			await self.channel_layer.group_send(
				self.room_group_name,
				{
					'type': 'game_over',
					'winner': 'player1' if self.goalsPlayer1 >= 5 else 'player2'
				}
			)
			matchObject = await sync_to_async(OnlineMatch.objects.get)(roomId=self.room_name)
			secret = os.environ.get("MATCHMAKER_SECRET")
			data = {
				'secret': secret,
				'matchId': self.room_name,
				'matchWinner': matchObject.player1 if self.goalsPlayer1 >= 5 else matchObject.player2,
				'matchLoser': matchObject.player2 if self.goalsPlayer1 >= 5 else matchObject.player1,
				'matchWinnerScore': self.goalsPlayer1 if self.goalsPlayer1 >= 5 else self.goalsPlayer2,
				'matchLoserScore': self.goalsPlayer2 if self.goalsPlayer1 >= 5 else self.goalsPlayer1
			}
			response = requests.post("http://flow:8000/api/match", data=json.dumps(data))
			if response.status_code != 201:
				print("Error sending match data to flow api")
			matchObject.hasCommenced = False
			await sync_to_async(matchObject.save)()


	###################################################################
	########################### CLIENT LOGIC ##########################
	###################################################################
	#-Utilized by host and guest instances

	################### CONNECT AND DISCONNECT WEBSOCKETS ##################
	async def connect(self):
		try:
			self.room_name = self.scope['url_route']['kwargs']['game_room']
			theMatchObject = await sync_to_async(OnlineMatch.objects.get)(roomId=self.room_name)
			self.room_group_name = 'match_%s' % self.room_name
			await self.channel_layer.group_add(
				self.room_group_name,
				self.channel_name
			)
			await self.accept()
			self.role = theMatchObject.playerCount
			theMatchObject.playerCount += 1
			if (self.role == 2): # handle second player connecting from invite
				theMatchObject.ready = True
			await sync_to_async(theMatchObject.save)()
			if self.role == 1:
				self.loopTaskActive = False
			if self.role > 2: # handle more than 2 players through invite
				await self.close()
		except OnlineMatch.DoesNotExist:
			print("Match object not found")
			return

	async def disconnect(self, close_code): # if the role 1 disconnects, the room closes for everyone. if role 2 disconnects, the room remains open but match object ready is set to false and player2 is set to empty and playerCount is decremented
		try:
			theMatchObject = await sync_to_async(OnlineMatch.objects.get)(roomId=self.room_name)
			matchObjectExists = True
		except:
			matchObjectExists = False
		try:
			if matchObjectExists:
				if theMatchObject.hasCommenced: # if the match has started send game over and record the match to flow api
					await self.channel_layer.group_send(
						self.room_group_name,
						{
							'type': 'game_over',
							'winner': 'player1' if self.role == 2 else 'player2'
						}
					)
					secret = os.environ.get("MATCHMAKER_SECRET")
					data = {
						'secret': secret,
						'matchId': self.room_name,
						'matchWinner': theMatchObject.player1 if self.role == 2 else theMatchObject.player2,
						'matchLoser': theMatchObject.player2 if self.role == 2 else theMatchObject.player1,
						'matchWinnerScore': 0,
						'matchLoserScore': 0
					}
					response = requests.post("http://flow:8000/api/match", data=json.dumps(data))
					if response.status_code != 201:
						print("Error sending match data to flow api")
				await self.channel_layer.group_send(
					self.room_group_name,
					{
						'type': 'room_closed'
					}
				)
				if (self.role == 1): # player 1 disconnects
					await sync_to_async(theMatchObject.delete)()
					if (self.loopTaskActive):
						self.loopTaskActive = False
						self.game_loop_task.cancel()
		
			# This happens anyway always when disconnecting
			await self.channel_layer.group_discard(
				self.room_group_name,
				self.channel_name
			)
			self.close()
		except:
			self.close()
			return

	################### RECEIVE DATA ON WEBSOCKETS ##################
	async def receive(self, text_data): # handle key presses up and down
		data = json.loads(text_data)
		if ('type' in data):
			if (data['type'] == 'key_press' and 'key' in data):
				if (data['key'] == 'up' or data['key'] == 'down'):
					if (self.role == 1):
						await self.channel_layer.group_send(
							self.room_group_name,
							{
								'type': 'key_press',
								'player1Paddle_y_change': data["key"]
							}
						)
					else:
						await self.channel_layer.group_send(
							self.room_group_name,
							{
								'type': 'key_press',
								'player2Paddle_y_change': data["key"]
							}
						)
			elif (data['type'] == 'room_data_request'):
				theMatchObject = await sync_to_async(OnlineMatch.objects.get)(roomId=self.room_name)
				await self.channel_layer.group_send(
					self.room_group_name,
					{
						'type': 'room_data',
						'player1': theMatchObject.player1,
						'player2': theMatchObject.player2
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
			elif (data['type'] == 'start_match' and 'ballSpeed' in data and 'paddleSpeed' in data): # will need to have metadata of the match, i.e. ball speed and paddle speed
				if (self.role != 1):
					await self.send(json.dumps({
						'identity': 'error',
						'message': 'Cannot start the match. You are not the host.'
					}))
				if (self.role == 1):#validate metaData
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
						print("Match initiated")
						theMatchObject = await sync_to_async(OnlineMatch.objects.get)(roomId=self.room_name)
						if theMatchObject.ready:
							ballSpeed = data['ballSpeed']
							paddleSpeed = data['paddleSpeed']
							theMatchObject.hasCommenced = True
							await sync_to_async(theMatchObject.save)()
							await self.init_match(ballSpeed, paddleSpeed)
							await self.initiate_start_match() # twice to ensure sync
							asyncio.sleep(0.5)
							await self.initiate_start_match()
							self.loopTaskActive = True
							self.game_loop_task = asyncio.create_task(self.pong())
						else:
							await self.send(json.dumps({
								'identity': 'error',
								'message': 'Not enough players to start the match.'
							}))
			else:
				await self.send(json.dumps({
					'identity': 'error',
					'message': 'Invalid data format'
				}))
		else:
			await self.send(json.dumps({
				'identity': 'error',
				'message': 'Invalid data format'
			}))


	################### SEND DATA ON WEBSOCKETS ##################
	#-Called by everyinstance in the group by group_send command
	async def room_data(self, event):
		await self.send(json.dumps({
			'identity': 'room_data',
			'player1': event['player1'],
			'player2': event['player2']
		}))

	async def room_closed(self, event):
		await self.send(json.dumps({
			'identity': 'room_closed'
		}))
		if (self.role == 1):
			try:
				theMatchObject = await sync_to_async(OnlineMatch.objects.get)(roomId=self.room_name)
				await sync_to_async(theMatchObject.delete)()
			except:
				print("Match object allready deleted")
			if self.loopTaskActive:
				self.loopTaskActive = False
				self.game_loop_task.cancel()

	async def live_message(self, event):
		await self.send(json.dumps({
			'identity': 'message',
			'message': event['message'],
			'sender': event['sender']
		}))
	
	async def key_press(self, event):
		if (self.role == 1 and self.loopTaskActive):
			if 'player1Paddle_y_change' in event:
				self.player1_update_queue.put(event['player1Paddle_y_change'])
			elif 'player2Paddle_y_change' in event:
				self.player2_update_queue.put(event['player2Paddle_y_change'])

	async def game_update(self, event):
		positions = event['positions']
		await self.send(json.dumps({
			'identity': 'game_update',
			'positions': positions
		}))
	
	async def game_over(self, event):
		await self.send(json.dumps({
			'identity': 'game_over',
			'winner': event['winner']
		}))
		if (self.role == 1):
			try:
				theMatchObject = await sync_to_async(OnlineMatch.objects.get)(roomId=self.room_name)
				await sync_to_async(theMatchObject.delete)()
			except:
				print("Match object allready deleted")
			if self.loopTaskActive:
				self.loopTaskActive = False
				self.game_loop_task.cancel()

	async def start_match(self, event):
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
			'goalsPlayer2': event['goalsPlayer2']
		}))