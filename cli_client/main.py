import os
import re
import time
import json
import requests
from source_files.config import Config, init_globals
from source_files.print_banners_docs import print_banner, print_available_commands
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def login(username, password):
	response = Config.session.post(Config.flowUrl + "/api/login", headers={"Content-Type": "application/json", "X-CSRFToken": Config.session.cookies["csrftoken"], "Referer": Config.flowReferer}, data=json.dumps({"username": username, "password": password}), verify=False)
	response.raise_for_status()

def logout():
	response = Config.session.post(Config.flowUrl + "/api/logout", headers={"Content-Type": "application/json", "X-CSRFToken": Config.session.cookies["csrftoken"], "Referer": Config.flowReferer}, verify=False)
	response.raise_for_status()

def main():
	print_banner()
	print_available_commands()
	while True:
		try:
			command = input("~CallOfPong: ")
			match command:
				case "exit":
					logout()
					print("Goodbye!")
					os._exit(0)
				case _:
					print("Invalid command. Please try again.")
		except:
			Config.openEditor = False
			if Config.currentWebSocket is not None:
				Config.currentWebSocket = None
			print("An error occurred. Please try again.")
			os.system('stty echo')
			continue

while True:
	os.system('clear')
	print_banner()
	try:
		hostIp = input("Please enter the host (example https://127.0.0.1:8008 ): ")
		init_globals(hostIp)
	except requests.exceptions.RequestException:
		print("Host IP invalid or service unavailable. Please try again.")
		time.sleep(Config.wait_time)
		continue
	break
while True:
	os.system('clear')
	print_banner()
	print("Please log in or create an account to continue.\n")
	try:
		userChoice = input("Would you like to create a new account or log in? Enter a command: (new, login): ")
		if (userChoice == "new"):
			while True:
				username = input("Enter your username: ")
				if len(username) < 4 or len(username) > 15:
					print("Username length must be 4-15 characters.")
					continue
				elif not re.fullmatch(r'^[a-zA-Z0-9]+$', username):
					print("Username must contain only alphanumeric characters.")
					continue
				break
			while True:
				email = input("Enter your email: ")
				if not email:
					print("Email is required.")
					continue
				elif not re.fullmatch(r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$', email):
					print("Email is invalid.")
					continue
				break
			os.system('stty -echo')
			while True:
				password = input("Enter your password: ")
				if not password:
					print("\nPassword is required.")
					continue
				elif len(password) < 5 or len(password) > 20:
					print("\nPassword length must be 5-20 characters.")
					continue
				elif not re.search(r'[A-Z]', password):
					print("\nPassword must contain at least one upper-case letter.")
					continue
				elif not re.search(r'[a-z]', password):
					print("\nPassword must contain at least one lower-case letter.")
					continue
				elif not re.search(r'[0-9]', password):
					print("\nPassword must contain at least one digit.")
					continue
				break
			while True:
				password2 = input("\nRe-enter your password: ")
				if password2 != password:
					print("\nPasswords do not match. Please try again.")
					continue
				break
			os.system('stty echo')
			response = Config.session.post(Config.flowUrl + "/api/user", headers={"Content-Type": "application/json", "X-CSRFToken": Config.session.cookies["csrftoken"], "Referer": Config.flowReferer}, data=json.dumps({"username": username, "email": email, "password": password, 'confirm_password': password2}), verify=False)
			response.raise_for_status()
			print("\nAccount created successfully. Please log in to continue.\n")
			time.sleep(Config.wait_time)
			continue
		elif (userChoice == "login"):
			username = input("Enter your username: ")
			os.system('stty -echo')
			password = input("Enter your password: ")
			os.system('stty echo')
			login(username, password)
		else:
			print("Invalid command. Please try again.")
			time.sleep(Config.wait_time)
			continue
	except requests.exceptions.HTTPError:
		print("\nInvalid username or password. Please try again.")
		time.sleep(Config.wait_time)
		continue
	print("\nLogin successful.")
	break
print("Getting your session...")
Config.username = username
time.sleep(Config.wait_time)
os.system('clear')
main()
