const url = '{{ response.url }}';
const username = '{{ username }}';
const blocklist = {{ blocked|safe }};
const gameMode = '{{ response.gameMode }}';
const ws = new WebSocket(url);
var game;
var role;
var host = false;
{% include "js/game.js" %}

ws.onopen = (event) => {
	ws.send(JSON.stringify({"type": "room_data_request"}))
};

ws.onmessage = async (event) => {

	const parsedMessage = JSON.parse(event.data);

	switch (parsedMessage.identity) {
		case "room_data":
			players.innerHTML = "";
			playersInRoom = [];
			if (parsedMessage.player1 === username)
				host = true
			playersInRoom.push(parsedMessage.player1);
			playersInRoom.push(parsedMessage.player2);
			playersInRoom.forEach((element) => {
				players.innerHTML += `<div class="player-name">${element}</div>`
			});
			break;

		case "error":
		case "message":
			if (blocklist.includes(parsedMessage.sender))
				break ;
			if (!('sender' in parsedMessage))
				parsedMessage.sender = 'Error';
			chatMessages.innerHTML += createChatMessageElement(parsedMessage);
			chatMessages.lastElementChild.scrollIntoView({ behavior: 'smooth', block: 'end'}); // scroll gracefully
			break;

		case "start_match":
			console.clear();
			gameContainer = document.getElementById("game-container");
			await changeContainerContent(document.body, "game");
			const canvas = document.getElementById("game-canvas");
			game = new Game(canvas, parsedMessage);
			role = (parsedMessage.player1 === username) ? 1 : 2;
			game.initKeyEvents();
			const interval = setInterval(() => game.draw(), 10);
			break;
		
		case "room_closed":
			// Example handling for room closed, such as closing the WebSocket connection
			console.log("Room closed");
			// Example: ws.close();
			break;
		case "setting_change":
			console.log("Setting change");
			slider.value = parsedMessage.value;
			value.innerHTML = parsedMessage.value;
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
			if (gameMode === "onlineTournament" || gameMode === "offlineTournament") {
				console.log("Game over");
				winnerMessage = {message: "Winner is: " + parsedMessage.winner, sender: "System"};
				chatMessages.innerHTML += createChatMessageElement(winnerMessage);
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
