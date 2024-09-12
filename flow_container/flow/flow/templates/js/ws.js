const url = '{{ response.url }}';
const username = '{{ username }}';
const blocklist = {{ blocked|safe }};
const gameMode = '{{ response.gameMode }}';
const ws = new WebSocket(url);

const wsErrorHandler = async (event) => {
	console.log("Websocket error!");
	const errorModal = document.getElementById("error-modal");
	errorModal.classList.add("show");
	await new Promise(resolve => setTimeout(resolve, 2500));
	window.location.hash = 'home';
}

ws.addEventListener("error", wsErrorHandler), { once: true };
ws.addEventListener("close", wsErrorHandler), { once: true };

let room_closed = false;
let matchLevel = 0;

{% include "js/game.js" %}

const game = new Game();
const canvas = document.getElementById("game-canvas");
game.initCanvas(canvas);

const lobbyContainer = document.getElementById("lobby-container");
const settingsContainer = document.getElementById("lobby-settings-container");
const gameContainer = document.getElementById("game-container");
const playerList = document.getElementById("lobby-player-list");
const chatMessages = document.getElementById('lobby-chat-messages');
const startButton = document.getElementById('lobby-start-button');

const player1Name = document.getElementById('player1-name');
const player2Name = document.getElementById('player2-name');
const player1Score = document.getElementById('player1-score');
const player2Score = document.getElementById('player2-score');

const displayModal = (text) => {
	const gameModal = document.getElementById("game-modal");
	gameModal.firstChild.textContent = text;
	gameModal.classList.add("show");
}

const isScrolledToBottom = () => {
	const threshold = 150;
	return chatMessages.scrollHeight - chatMessages.scrollTop - threshold <= chatMessages.clientHeight;
};

const sendSystemMessage = (username, mode) => {
	let msg;
	switch (mode) {
		case "tournie_winner":
			msg = {message: "Tournament winner is: " + username, sender: "System"};
			break;
		case "winner":
			msg = {message: "Winner is: " + username, sender: "System"};
			break;
		case "closed":
			msg = {message: "Room closed: " + username + " disconnected!", sender: "System"};
			break;
		case "disconnect":
			msg = {message: username + " disconnected!", sender: "System"};
			break;
		case "cannot":
			msg = {message: "Cannot start: Room closed!", sender: "System"};
	}
	chatMessages.appendChild(createChatMessageElement(msg));
	if (isScrolledToBottom())
		chatMessages.lastElementChild.scrollIntoView({ behavior: 'smooth', block: 'end'});
}

ws.onopen = (event) => {
	if (gameMode === "onlineTournament" || gameMode === "online")
		ws.send(JSON.stringify({"type": "room_data_request"}));
	addEventListener("hashchange", (event) => {
		ws.removeEventListener("close", wsErrorHandler);
		ws.close();
		game.stopKeyEvents();
	},
	{ once: true });
	addEventListener("beforeunload", (event) => {
		ws.removeEventListener("close", wsErrorHandler);
		ws.close();
	});
};

ws.onmessage = async (event) => {

	const parsedMessage = JSON.parse(event.data);

	switch (parsedMessage.identity) {
		case "room_data":
			playerList.textContent = "";
			playersInRoom = [];
			if ((gameMode === "online" || gameMode === "onlineTournament") && parsedMessage.player1 !== username) {
				speedSlider.setAttribute("disabled", "true");
				startButton.setAttribute("disabled", "true");
			}
			playersInRoom.push(parsedMessage.player1);
			playersInRoom.push(parsedMessage.player2);
			if (gameMode === "onlineTournament" || gameMode === "localTournament") {
				playersInRoom.push(parsedMessage.player3);
				playersInRoom.push(parsedMessage.player4);
			}
			playersInRoom.forEach((player) => {
				if (player) {
					const playerElement = document.createElement('div');
					playerElement.classList.add('lobby-player-name');

					if (gameMode === "online" || gameMode === "onlineTournament") {
						const playerAvatarContainer = document.createElement('div');
						playerAvatarContainer.classList.add('avatar');
						const playerAvatarImage = document.createElement('img');
						playerAvatarImage.src = "/api/avatar?username=" + player;
						playerAvatarContainer.appendChild(playerAvatarImage);
						playerElement.appendChild(playerAvatarContainer);
					}

					const playerName = document.createElement('span');
					playerName.textContent = player;
					playerElement.appendChild(playerName);

					playerList.appendChild(playerElement);
				}
			});
			break;

		case "error":
		case "message":
			if (blocklist.includes(parsedMessage.sender))
				break ;
			if (!('sender' in parsedMessage))
				parsedMessage.sender = 'Error';
			chatMessages.appendChild(createChatMessageElement(parsedMessage));
			if (isScrolledToBottom())
				chatMessages.lastElementChild.scrollIntoView({ behavior: 'smooth', block: 'end'}); // scroll gracefully
			break;

		case "start_match":
			player1Name.textContent = parsedMessage.player1_username;
			player2Name.textContent = parsedMessage.player2_username;
			lobbyContainer.classList.add("hide");
			settingsContainer.classList.add("hide");
			gameContainer.classList.remove("hide");
			game.initStartValues(parsedMessage);
			game.initKeyEvents();
			game.startRedraw();
			ws.send(JSON.stringify({"type": "received_start_match"}));
			addEventListener("hashchange", (event) => {
				game.stopRedraw();
			},
			{ once: true });
			break;

		case "room_closed":
			console.log("Room closed: " + parsedMessage.username + " disconnected!");
			sendSystemMessage(parsedMessage.username, "closed");
			if (lobbyContainer.classList.contains("hide") && gameMode == "onlineTournament" && !room_closed)
				displayModal("Tournament closed: Host disconnected");
			room_closed = true;
			break;

		case "setting_change":
			console.log("Setting change");
			speedSlider.value = parsedMessage.value;
			speedSliderValBelow.textContent = parsedMessage.value / 10;
			break;

		case "game_update":
			try {
				game.updateValues(parsedMessage.positions);
				if (parsedMessage.positions.goalsPlayer1 != player1Score.textContent)
					player1Score.textContent = parsedMessage.positions.goalsPlayer1;
				if (parsedMessage.positions.goalsPlayer2 != player2Score.textContent)
					player2Score.textContent = parsedMessage.positions.goalsPlayer2;
			} catch (TypeError) {
				console.log('game_update: game not ready yet');
			}
			break;

		case "tournament_over":
			console.log("Tournament over");
			sendSystemMessage(parsedMessage.winner, "tournie_winner");
			displayModal("Tournament winner: " + parsedMessage.winner);
			room_closed = true;
			break;

		case "game_over":
			game.stopRedraw();
			game.stopKeyEvents();
			if (gameMode === "onlineTournament" || gameMode === "localTournament") {
				if (matchLevel++ < 2) {
					console.log("Game over");
					lobbyContainer.classList.remove("hide");
					gameContainer.classList.add("hide");
					sendSystemMessage(parsedMessage.winner, "winner");
				}
			}
			else {
				console.log("Game over");
				displayModal("Match winner: " + parsedMessage.winner);
			}
			break;

		case "player_disconnected":
			console.log(parsedMessage.username + " disconnected!");
			sendSystemMessage(parsedMessage.username, "disconnect");
			break;

		default:
			console.log("Unknown message identity: " + parsedMessage.identity);
	}
};
