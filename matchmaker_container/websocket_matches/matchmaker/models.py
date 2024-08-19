from django.db import models

# Create your models here.
class OnlineMatch(models.Model):
	roomId = models.CharField(max_length=200)
	playerCount = models.IntegerField(default=1)

	ready = models.BooleanField(default=False)
	hasCommenced = models.BooleanField(default=False)

	player1 = models.CharField(max_length=15)
	player2 = models.CharField(max_length=15)

class OnlineTournament(models.Model):
	roomId = models.CharField(max_length=36)
	playerCount = models.IntegerField(default=1)

	ready = models.BooleanField(default=False)
	hasCommenced = models.BooleanField(default=False)

	player1 = models.CharField(max_length=15)
	player2 = models.CharField(max_length=15)
	player3 = models.CharField(max_length=15)
	player4 = models.CharField(max_length=15)

class LocalMatch(models.Model):
	roomId = models.CharField(max_length=36)
	player1 = models.CharField(max_length=15)
	player2 = models.CharField(max_length=15)

class LocalTournament(models.Model):
	roomId = models.CharField(max_length=200)
	player1 = models.CharField(max_length=15)
	player2 = models.CharField(max_length=15)
	player3 = models.CharField(max_length=15)
	player4 = models.CharField(max_length=15)
