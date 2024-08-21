{
	{% include "js/ws.js" %}

	const chatInput = document.getElementById('lobby-chat-input');
	const inviteInput = document.getElementById('lobby-invite-input');
	const chatInputForm = document.getElementById('lobby-chat-input-form');
	const startButton = document.getElementById('lobby-start-button');
	const inviteButton = document.getElementById('lobby-invite-button');

	var host = false;

	const createChatMessageElement = (message) => `
	<div class="message">
		<div class="message-sender">${message.sender}</div>
		<div class="message-text">${message.message}</div>
	</div>
	`

	const sendMessage = (e) => {
		e.preventDefault(); // prevent page reload when message is sent

		ws.send(JSON.stringify({"type": "message", "message": chatInput.value, "sender": username}));

		chatInputForm.reset();
	};

	chatInputForm.addEventListener('submit', (e) => {
		e.preventDefault();
		const message = chatInput.value.trim();

		if (message) {
			sendMessage(e);
			chatInput.value = '';
		}
	});

	startButton.addEventListener('click', (e) => {
		e.preventDefault();
		const ballSpeed = value.innerHTML / 1000;
		const paddleSpeed = ballSpeed;
		console.log(ballSpeed);
		console.log(paddleSpeed);
		if (gameMode === "onlineTournament" || gameMode === "localTournament")
			ws.send(JSON.stringify({"type": "start_tournament", "ballSpeed": ballSpeed, "paddleSpeed": paddleSpeed}));
		else
			ws.send(JSON.stringify({"type": "start_match", "ballSpeed": ballSpeed, "paddleSpeed": paddleSpeed}));
	});

	inviteButton.addEventListener('click', (e) => {
		e.preventDefault();
		receiver = inviteInput.value.trim();
		ws.send(JSON.stringify({"type": "invite", "receiver": receiver}));
	});

	var slider = document.getElementById("myRange");
	var value = document.getElementById("value"); // change name
	value.innerHTML = slider.value; // Display the default slider value 

	// Update the current slider value (each time you drag the slider handle)
	slider.oninput = function() {
		if (host === true)
			ws.send(JSON.stringify({"type": "setting_change", "value": this.value}));
		else
			this.value = value.innerHTML;
	}

	chatInput.focus();
}
