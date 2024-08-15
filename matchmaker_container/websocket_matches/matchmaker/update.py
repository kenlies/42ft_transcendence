from matchmaker.constants import PADDLE_HEIGHT, COURT_HEIGHT, COURT_WIDTH
import random
import math

async def update_players(self):
	while not self.player1_update_queue.empty(): # check that the bottom and top dont go over court height
		temp = self.player1_update_queue.get()
		if (temp < 0):
			self.player1Paddle_y_top = 0
		elif (temp + PADDLE_HEIGHT > 1):
			self.player1Paddle_y_top = 1 - PADDLE_HEIGHT
		else:
			self.player1Paddle_y_top = temp
	while not self.player2_update_queue.empty():
		temp = self.player2_update_queue.get()
		if (temp < 0):
			self.player2Paddle_y_top = 0
		elif (temp + PADDLE_HEIGHT > 1):
			self.player2Paddle_y_top = 1 - PADDLE_HEIGHT
		else:
			self.player2Paddle_y_top = temp

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
		self.ballDeltaY = randomFactor
		self.ballDeltaX = math.sqrt((self.ballSpeed ** 2) - (self.ballDeltaY ** 2))
	elif (self.ball_x >= self.player2Paddle_x and self.ball_y >= self.player2Paddle_y_top and self.ball_y <= self.player2Paddle_y_top + PADDLE_HEIGHT):
		self.ballDeltaY = randomFactor
		self.ballDeltaX = math.sqrt((self.ballSpeed ** 2) - (self.ballDeltaY ** 2)) * -1
