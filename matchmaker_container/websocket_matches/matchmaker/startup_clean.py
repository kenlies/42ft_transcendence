from .models import OnlineMatch, OnlineTournament, LocalMatch, LocalTournament

def clean():#when starting the server, clean all the matches and tournaments. This is to ensure that no objects exist if the server was shut down abruptly
	OnlineMatch.objects.all().delete()
	OnlineTournament.objects.all().delete()
	LocalMatch.objects.all().delete()
	LocalTournament.objects.all().delete()
