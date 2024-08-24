from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta, datetime
from django.utils import timezone

class Account(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	avatar = models.ImageField(upload_to='api/static/avatars/')
	friendList = models.ManyToManyField('self', blank=True)
	blockedList = models.ManyToManyField('self', blank=True)
	matchHistory = models.ManyToManyField('Match', through='MatchRecords', blank=True)
	sentMessages = models.ManyToManyField('Message', blank=True, related_name='sent_messages')
	receivedMessages = models.ManyToManyField('Message', blank=True, related_name='received_messages')
	last_activity = models.DateTimeField(default=datetime.min)

	def __str__(self):
		return self.user.username

	@property
	def is_online(self):
		return timezone.now() < self.last_activity + timedelta(minutes=1)

class Match(models.Model):
	matchId = models.CharField(max_length=50)
	matchDate = models.CharField(max_length=50, default='')
	matchWinnerUsername = models.CharField(max_length=15, default='')
	matchLoserUsername = models.CharField(max_length=15, default='')
	matchWinnerScore = models.IntegerField()
	matchLoserScore = models.IntegerField()

class MatchRecords(models.Model):
	account = models.ForeignKey(Account, on_delete=models.CASCADE)
	match = models.ForeignKey(Match, on_delete=models.CASCADE)
	opponent = models.CharField(max_length=15)
	score =  models.CharField(max_length=5)
	result = models.CharField(max_length=5)

class Message(models.Model):
	messageContent = models.CharField(max_length=500)
	messageSender = models.ForeignKey(Account, on_delete=models.CASCADE, blank=False, null=False, related_name='message_sender')
	messageReceiver = models.ForeignKey(Account, on_delete=models.CASCADE, blank=False, null=False, related_name='message_receiver')
	messageDate = models.CharField(max_length=50, default='')
