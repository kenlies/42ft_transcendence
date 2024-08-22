import os
import json
import requests
from .config import Config
from .print_banners_docs import print_banner, print_available_commands

def view_me():
	os.system('clear')
	print_banner()
	print_available_commands()
	print("Getting your user information...\n")
	response = Config.session.get(Config.flowUrl + "/api/user?username=" + Config.username, headers={"Content-Type": "application/json", "X-CSRFToken": Config.session.cookies["csrftoken"], "session-id": Config.session.cookies["sessionid"], "Referer": Config.flowReferer}, verify=False)
	response.raise_for_status()
	toPrintUsername = response.json()["username"]
	toPrintEmail = response.json()["email"]
	toPrintFriends = response.json()["friends"]
	toPrintBlocked = response.json()["blocked"]
	toPrintMatches = response.json()["matches"]
	if toPrintFriends == []:
		toPrintFriends = ["No friends yet."]
	if toPrintBlocked == []:
		toPrintBlocked = ["No blocked users yet."]
	if toPrintMatches == []:
		toPrintMatches = None
	avatarEndpoint = response.json()["avatar_url"]
	avatarResponse = Config.session.get(Config.flowUrl + "" + avatarEndpoint, headers={"Content-Type": "application/json", "X-CSRFToken": Config.session.cookies["csrftoken"], "session-id": Config.session.cookies["sessionid"], "Referer": Config.flowReferer}, verify=False)
	avatar = avatarResponse.content
	print("-----------------------------------------------------------------------------------------------------------------------")
	print("|                                                      MY USER DATA                                                   |")
	print("-----------------------------------------------------------------------------------------------------------------------")
	print("|                                                                                                                     |")
	print("  Username: " + toPrintUsername)
	print("  Email: " + toPrintEmail)
	print("\n  Friends: ")
	for friend in toPrintFriends:
		print("	" + friend)
	print("\n  Blocked: ")
	for blocked in toPrintBlocked:
		print("	" + blocked)
	print("\n  Matches: ")
	if toPrintMatches == None:
		print("	No matches yet.")
	else:
		for match in toPrintMatches:
			print("	" + "Id: " + match['matchId'])
			print("	" + "Date: " + match['matchDate'])
			print("	" + "Winner: " + match['matchWinner'] + ". With the score: " + str(match['matchWinnerScore']) + " - " + str(match['matchLoserScore']) +  ". Against: " + match['matchLoser'] + ".\n")
	print("|                                                                                                                     |")
	print("-----------------------------------------------------------------------------------------------------------------------\n")
	yesOrNo = input("Would you like to download your avatar? (y/n): ")
	if yesOrNo == "y" or yesOrNo == "Y" or yesOrNo == "yes" or yesOrNo == "Yes":
		with open("avatar.png", "wb") as f:
			f.write(avatar)
			print("Avatar downloaded as avatar.png\n")
	else:
		print("Avatar not downloaded.\n")
