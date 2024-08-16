from matchmaker.constants import PADDLE_HEIGHT, COURT_HEIGHT, COURT_WIDTH
import random

async def update_players(self):
	while not self.player1_update_queue.empty(): # check that the bottom and top dont go over court height
		temp = self.player1_update_queue.get()
		if (temp == 'up'):
			if (self.player1Paddle_y_top - self.paddleSpeed >= 0):
				self.player1Paddle_y_top -= self.paddleSpeed
			else:
				self.player1Paddle_y_top = 0
		elif (temp == 'down'):
			if (self.player1Paddle_y_top + PADDLE_HEIGHT + self.paddleSpeed <= self.courtHeight):
				self.player1Paddle_y_top += self.paddleSpeed
			else:
				self.player1Paddle_y_top = self.courtHeight - PADDLE_HEIGHT
	while not self.player2_update_queue.empty():
		temp = self.player2_update_queue.get()
		if (temp == 'up'):
			if (self.player2Paddle_y_top - self.paddleSpeed >= 0):
				self.player2Paddle_y_top -= self.paddleSpeed
			else:
				self.player2Paddle_y_top = 0
		elif (temp == 'down'):
			if (self.player2Paddle_y_top + PADDLE_HEIGHT + self.paddleSpeed <= self.courtHeight):
				self.player2Paddle_y_top += self.paddleSpeed
			else:
				self.player2Paddle_y_top = self.courtHeight - PADDLE_HEIGHT

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
