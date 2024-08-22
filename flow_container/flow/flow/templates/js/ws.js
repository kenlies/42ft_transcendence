const url = '{{ response.url }}';
const username = '{{ username }}';
const blocklist = {{ blocked|safe }};
const gameMode = '{{ response.gameMode }}';
const ws = new WebSocket(url);
let game;
let role;
let host = false;
let gameDrawInterval;

{% include "js/game.js" %}

const lobbyContainer = document.getElementById("lobby-container");
const settingsContainer = document.getElementById("settings-container");
const gameContainer = document.getElementById("game-container");
const playerContainer = document.getElementById("player-container");
const chatMessages = document.getElementById('lobby-chat-messages');

ws.onopen = (event) => {
	ws.send(JSON.stringify({"type": "room_data_request"}))
	addEventListener("hashchange", (event) => {
		ws.close();
	},
	{ once: true });
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
			const messageElement = createChatMessageElement(parsedMessage);
			chatMessages.appendChild(messageElement);
			chatMessages.lastElementChild.scrollIntoView({ behavior: 'smooth', block: 'end'}); // scroll gracefully
			break;

		case "start_match":
			console.clear();
			lobbyContainer.classList.add("hide");
			settingsContainer.classList.add("hide");
			gameContainer.classList.remove("hide");
			await changeContainerContent(gameContainer, "game");
			const canvas = document.getElementById("game-canvas");
			game = new Game(canvas, parsedMessage);
			role = (parsedMessage.player1 === username) ? 1 : 2;
			game.initKeyEvents();
			gameDrawInterval = setInterval(() => game.draw(), 10);
			addEventListener("hashchange", (event) => {
				clearInterval(gameDrawInterval);
			},
			{ once: true });
			break;

		case "room_closed":
			// Example handling for room closed, such as closing the WebSocket connection
			console.log("Room closed");
			// Example: ws.close();
			break;
		case "setting_change":
			console.log("Setting change");
			slider.value = parsedMessage.value;
			value.textContent = parsedMessage.value;
			break;
		case "game_update":
			try {
				game.updateValues(parsedMessage.positions);
			} catch (TypeError) {
				console.log('game_update: game not ready yet')
			}
			break;
		case "tournament_over":
			//same as game_over on 1v1
			console.log("Tournament over");
			break;
		case "game_over":
			clearInterval(gameDrawInterval);
			if (gameMode === "onlineTournament" || gameMode === "offlineTournament") {
				console.log("Game over");
				lobbyContainer.classList.remove("hide");
				gameContainer.classList.add("hide");
				const winnerMessage = {message: "Winner is: " + parsedMessage.winner, sender: "System"};
				chatMessages.appendChild(createChatMessageElement(winnerMessage));
				chatMessages.lastElementChild.scrollIntoView({ behavior: 'smooth', block: 'end'});
			}
			else {
				//1v1 logic. Show winner screen. Go home.
				console.log("Game over");
				break;
			}

		default:
			console.log("Unknown message identity: " + parsedMessage.identity);
	}
};
