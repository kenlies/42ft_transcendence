{
	{% include "js/ws.js" %}

	const chatInput = document.getElementById('lobby-chat-input');
	const inviteInput = document.getElementById('lobby-invite-input');
	const chatInputForm = document.getElementById('lobby-chat-input-form');
	const startButton = document.getElementById('lobby-start-button');
	const inviteButton = document.getElementById('lobby-invite-button');

	const createChatMessageElement = (message) => {
		const messageElement = document.createElement('div');
		messageElement.classList.add('message');

		const senderElement = document.createElement('div');
		senderElement.classList.add('message-sender');
		senderElement.textContent = message.sender;

		const textElement = document.createElement('div');
		textElement.classList.add('message-text');
		textElement.textContent = message.message;

		messageElement.appendChild(senderElement);
		messageElement.appendChild(textElement);

		return messageElement;
	};

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
		const ballSpeed = speedSliderValBelow.textContent / 1000;
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

	const speedSlider = document.getElementById("speed-slider");
	const speedSliderValBelow = document.getElementById("speed-slider-val-below"); // change name
	speedSliderValBelow.textContent = speedSlider.value; // Display the default slider value

	// Update the current slider value (each time you drag the slider handle)
	speedSlider.oninput = function() {
		if (host === true)
			ws.send(JSON.stringify({"type": "setting_change", "value": this.value}));
		else
			this.value = speedSliderValBelow.textContent;
	}

	chatInput.focus();
}
