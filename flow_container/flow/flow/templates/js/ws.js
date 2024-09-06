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
const settingsContainer = document.getElementById("settings-container");
const gameContainer = document.getElementById("game-container");
const playerContainer = document.getElementById("player-container");
const chatMessages = document.getElementById('lobby-chat-messages');

const startButton = document.getElementById('lobby-start-button');

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
			playerContainer.textContent = "";
			playersInRoom = [];
			if ((gameMode === "online" || gameMode === "onlineTournament") && parsedMessage.player1 !== username)
				speedSlider.setAttribute("disabled", "true");
			playersInRoom.push(parsedMessage.player1);
			playersInRoom.push(parsedMessage.player2);
			if (gameMode === "onlineTournament" || gameMode === "localTournament") {
				playersInRoom.push(parsedMessage.player3);
				playersInRoom.push(parsedMessage.player4);
			}
			playersInRoom.forEach((element) => {
				const playerElement = document.createElement('div');
				playerElement.classList.add('player-name');
				playerElement.textContent = element;
				playerContainer.appendChild(playerElement);
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
			console.clear();
			lobbyContainer.classList.add("hide");
			settingsContainer.classList.add("hide");
			gameContainer.classList.remove("hide");
			game.initStartValues(parsedMessage);
			game.initKeyEvents();
			game.startRedraw();
			addEventListener("hashchange", (event) => {
				game.stopRedraw();
			},
			{ once: true });
			break;

		case "room_closed":
			console.log("Room closed: " + parsedMessage.username + " disconnected!");
			sendSystemMessage(parsedMessage.username, "closed");
			room_closed = true;
			if (lobbyContainer.classList.contains("hide") && gameMode == "onlineTournament") {
				await new Promise(resolve => setTimeout(resolve, 5000));
				displayModal("Tournament closed: Host disconnected");
			}
			break;

		case "setting_change":
			console.log("Setting change");
			speedSlider.value = parsedMessage.value;
			speedSliderValBelow.textContent = parsedMessage.value / 10;
			break;

		case "game_update":
			try {
				game.updateValues(parsedMessage.positions);
			} catch (TypeError) {
				console.log('game_update: game not ready yet');
			}
			break;

		case "tournament_over":
			console.log("Tournament over");
			sendSystemMessage(parsedMessage.winner, "tournie_winner");
			displayModal("Tournament winner: " + parsedMessage.winner);
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
