const url = '{{ response.url }}';
const username = '{{ username }}';
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

		default:
			console.log("Unknown message identity: " + parsedMessage.identity);
	}
};
