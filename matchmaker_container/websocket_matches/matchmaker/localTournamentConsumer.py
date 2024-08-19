import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import LocalTournament
from asgiref.sync import sync_to_async
import asyncio
from queue import Queue
import random

from matchmaker.update import update_players, update_ball
from matchmaker.constants import PADDLE_HEIGHT, COURT_HEIGHT, COURT_WIDTH

class LocalTournamentConsumer(AsyncWebsocketConsumer):

	async def init_match_meta_data(self, ballSpeed, paddleSpeed):
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

	################### CONNECT AND DISCONNECT WEBSOCKETS ##################
	async def connect(self):
		try:
			self.room_name = self.scope['url_route']['kwargs']['game_room']
			thetournament = await sync_to_async(LocalTournament.objects.get)(roomId=self.room_name)
			self.player1 = thetournament.player1
			self.player2 = thetournament.player2
			self.player3 = thetournament.player3
			self.player4 = thetournament.player4
			self.loopTaskActive = False
			await self.accept()
		except thetournament.DoesNotExist:
			print("Match object not found")
			return
		
	async def disconnect(self, close_code):
		try:
			await sync_to_async(LocalTournament.objects.get)(roomId=self.room_name).delete()
			if (self.loopTaskActive):
				self.loopTaskActive = False
				self.game_loop_task.cancel()
		except:
			if (self.loopTaskActive):
				self.loopTaskActive = False
				self.game_loop_task.cancel()
		self.close()


	############ GAME LOGIC ############

	async def send_start_match(self):
		await self.send(json.dumps({
				'identity': 'start_match',
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
		}))

	async def single_match(self, player1, player2):
		self.gameOnGoing = True
		self.currentPLayer1 = player1
		self.currentPLayer2 = player2
		for _ in range(2):
			await self.send_start_match()
			await asyncio.sleep(1)
		while (self.goalsPlayer1 < 5 and self.goalsPlayer2 < 5):
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
			await self.send(json.dumps({
				'identity': 'game_update',
				'positions': positions
			}))
			await asyncio.sleep(0.01)
		await self.send(json.dumps({
			'identity': 'game_over',
			'winner': self.get_username_from_role(player1) if self.goalsPlayer1 >= 5 else self.get_username_from_role(player2)
		}))
		self.gameOnGoing = False
		return player1 if self.goalsPlayer1 >= 5 else player2

	async def tournament(self):
		await asyncio.sleep(0.01)
		shuffled = [1, 2, 3, 4]
		random.shuffle(shuffled)
		self.firstLevelMatch1 = [shuffled[0], shuffled[1]]
		self.firstLevelMatch2 = [shuffled[2], shuffled[3]]
		theTournament = await sync_to_async(LocalTournament.objects.get)(roomId=self.room_name)
		self.player1Username = theTournament.player1
		self.player2Username = theTournament.player2
		self.player3Username = theTournament.player3
		self.player4Username = theTournament.player4
		await self.send(json.dumps({
			'identity': 'message',
			'message': 'First level matches are about to begin. The first match is between ' + self.get_username_from_role(self.firstLevelMatch1[0]) + ' and ' + self.get_username_from_role(self.firstLevelMatch1[1]),
			'sender': 'System'
		}))
		await asyncio.sleep(5)
		self.match1Winner = await self.single_match(self.firstLevelMatch1[0], self.firstLevelMatch1[1])
		await self.reset_match_data()
		await asyncio.sleep(2)
		await self.send(json.dumps({
			'identity': 'message',
			'message': 'The second match is between ' + self.get_username_from_role(self.firstLevelMatch2[0]) + ' and ' + self.get_username_from_role(self.firstLevelMatch2[1]),
			'sender': 'System'
		}))
		await asyncio.sleep(5)
		self.match2Winner = await self.single_match(self.firstLevelMatch2[0], self.firstLevelMatch2[1])
		await self.reset_match_data()
		await asyncio.sleep(5)
		await self.send(json.dumps({
			'identity': 'message',
			'message': 'The final match is between ' + self.get_username_from_role(self.match1Winner) + ' and ' + self.get_username_from_role(self.match2Winner),
			'sender': 'System'
		}))
		await asyncio.sleep(5)
		self.tournamentWinner = await self.single_match(self.match1Winner, self.match2Winner)
		await self.reset_match_data()
		await asyncio.sleep(5)
		await self.send(json.dumps({
			'identity': 'tournament_over',
			'winner': self.get_username_from_role(self.tournamentWinner)
		}))
		
	################### RECEIVE DATA ON WEBSOCKETS ##################
	async def receive(self, text_data):
		data = json.loads(text_data)
		if ('type' in data):
			if (self.loopTaskActive and self.gameOnGoing):
				if (data['type'] == 'paddle_position' and 'value' in data and 'player' in data):
					if (data['player'] == 'player1'):
						self.player1_update_queue.put(data['value'])
					elif (data['player'] == 'player2'):
						self.player2_update_queue.put(data['value'])
			elif (data['type'] == 'start_tournament' and 'ballSpeed' in data and 'paddleSpeed' in data):
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
					theTournament = await sync_to_async(LocalTournament.objects.get)(roomId=self.room_name)
					ballSpeed = data['ballSpeed']
					paddleSpeed = data['paddleSpeed']
					theTournament.hasCommenced = True
					await sync_to_async(theTournament.save)()
					await self.init_match_meta_data(ballSpeed, paddleSpeed)
					await self.send(json.dumps({
						'identity': 'message',
						'message': 'Tournament has started. Get ready!',
						'sender': 'System'
					}))
					self.loopTaskActive = True
					self.game_loop_task = asyncio.create_task(self.tournament())
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
