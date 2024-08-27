const url = '{{ response.url }}';
const username = '{{ username }}';
const blocklist = {{ blocked|safe }};
const gameMode = '{{ response.gameMode }}';
const ws = new WebSocket(url);
let host = false;
let matchLevel = 0;

{% include "js/game.js" %}

const game = new Game();

const lobbyContainer = document.getElementById("lobby-container");
const settingsContainer = document.getElementById("settings-container");
const gameContainer = document.getElementById("game-container");
const playerContainer = document.getElementById("player-container");
const chatMessages = document.getElementById('lobby-chat-messages');

const displayWinner = (text) => {
	const gameModal = document.getElementById("game-modal");
	gameModal.firstChild.textContent = text;
	gameModal.classList.add("show");
}

const sendSystemMessage = (username, mode) => {
	let msg;
	if (mode === "winner")
		msg = {message: "Winner is: " + username, sender: "System"};
	else if (mode === "closed")
		msg = {message: "Room closed: " + username + " disconnected!", sender: "System"};
	else
		msg = {message: username + " disconnected!", sender: "System"};
	chatMessages.appendChild(createChatMessageElement(msg));
	chatMessages.lastElementChild.scrollIntoView({ behavior: 'smooth', block: 'end'});
}

ws.onopen = (event) => {
	if (gameMode === "onlineTournament" || gameMode === "online")
		ws.send(JSON.stringify({"type": "room_data_request"}))
	addEventListener("hashchange", (event) => {
		ws.close();
		game.stopKeyEvents();
	},
	{ once: true });
	addEventListener("beforeunload", (event) => {
		ws.close();
	});
};

ws.onmessage = async (event) => {

	const parsedMessage = JSON.parse(event.data);

	switch (parsedMessage.identity) {
		case "room_data":
			playerContainer.textContent = "";
			playersInRoom = [];
			if (parsedMessage.player1 === username)
				host = true
			playersInRoom.push(parsedMessage.player1);
			playersInRoom.push(parsedMessage.player2);
			if (gameMode === "onlineTournament") {
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
			chatMessages.lastElementChild.scrollIntoView({ behavior: 'smooth', block: 'end'}); // scroll gracefully
			break;

		case "start_match":
			console.clear();
			lobbyContainer.classList.add("hide");
			settingsContainer.classList.add("hide");
			gameContainer.classList.remove("hide");
			await changeContainerContent(gameContainer, "game");
			const canvas = document.getElementById("game-canvas");
			game.initCanvas(canvas);
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
			break;

		case "setting_change":
			console.log("Setting change");
			speedSlider.value = parsedMessage.value;
			speedSliderValBelow.textContent = parsedMessage.value;
			break;

		case "game_update":
			try {
				game.updateValues(parsedMessage.positions);
			} catch (TypeError) {
				console.log('game_update: game not ready yet')
			}
			break;

		case "tournament_over":
			console.log("Tournament over");
			displayWinner("Tournament winner: " + parsedMessage.winner);
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
				displayWinner("Match winner: " + parsedMessage.winner);
			}
			break;

		case "player_disconnected":
			console.log(parsedMessage.username + " disconnected!");
			sendSystemMessage(parsedMessage.username, "dc");
			break;

		default:
			console.log("Unknown message identity: " + parsedMessage.identity);
	}
};
