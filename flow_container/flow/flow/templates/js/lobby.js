{
	{% include "js/ws.js" %}

	const chatInput = document.getElementById('lobby-chat-input');
	const chatInputForm = document.getElementById('lobby-chat-input-form');

    const modalDialog = document.getElementById('modal-dialog-container');
    const modalDialogContent = document.getElementById('modal-dialog-content');
    const modalDialogClose = document.getElementById('modal-dialog-close');
    modalDialogClose.addEventListener('click', (event) => {
		modalDialog.classList.remove("show");
    });

	{% if response.gameMode == 'online' or response.gameMode == 'onlineTournament' %}
		const inviteButton = document.getElementById('invite-player-button');
		inviteButton.addEventListener('click', async (event) => {
			event.preventDefault();
			await changeContainerContent(modalDialogContent, 'dialogs/lobby_invite_form');
			modalDialog.classList.add("show");

			const inviteForm = document.getElementById('lobby-invite-form');
			const inviteError = document.getElementById('lobby-invite-error');
			const inviteInput = document.getElementById('lobby-invite-input');

			inviteForm.addEventListener('submit', async (event) => {
				event.preventDefault();
				receiver = inviteInput.value.trim();

				if (receiver == '{{ user.username }}') {
					inviteError.textContent = 'Can not invite yourself!';
					inviteError.classList.add("show");
					return;
				}

				try {
					const response = await fetch('/api/user?' + new URLSearchParams({
						username: receiver,
					}).toString());

					if (response.ok) {
						console.log('Invite sent to ' + receiver);
						ws.send(JSON.stringify({"type": "invite", "receiver": receiver}));
						modalDialog.classList.remove("show");
					}
					else {
						inviteError.textContent = await response.text();
						inviteError.classList.add("show");
					}
				}
				catch (error) {
					inviteError.textContent = error;
					inviteError.classList.add("show");
				}
			});
		});
	{% endif %}

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

	if (gameMode === "local" || gameMode === "localTournament" || gameMode === "ai")
	{
		/* const inviteButton = document.getElementById('invite-player-button');
		inviteButton.disabled = true; */

		if (gameMode === "local" || gameMode === "ai") {
			const chat = document.getElementById('lobby-chat-container');

			chat.classList.add("hide");
		}
		else {
			chatInputForm.classList.add("hide");
		}
	}
	else { // only add listeners on chat/invite buttons for online games
		chatInputForm.addEventListener('submit', (e) => {
			e.preventDefault();
			const message = chatInput.value.trim();

			if (message) {
				sendMessage(e);
				chatInput.value = '';
			}
		});
	}

	startButton.addEventListener('click', (e) => {
		e.preventDefault();
		if (room_closed) {
			sendSystemMessage(null, "cannot");
			return ;
		}
		const ballSpeed = speedSlider.value / 1000;
		const paddleSpeed = ballSpeed;
		console.log(ballSpeed);
		console.log(paddleSpeed);
		if (gameMode === "onlineTournament" || gameMode === "localTournament")
			ws.send(JSON.stringify({"type": "start_tournament", "ballSpeed": ballSpeed, "paddleSpeed": paddleSpeed}));
		else
			ws.send(JSON.stringify({"type": "start_match", "ballSpeed": ballSpeed, "paddleSpeed": paddleSpeed}));
	});

	const speedSlider = document.getElementById("speed-slider");
	const speedSliderValBelow = document.getElementById("speed-slider-val-below"); // change name
	speedSliderValBelow.textContent = speedSlider.value / 10; // Display the default slider value

	// Update the current slider value (each time you drag the slider handle)
	speedSlider.oninput = function() {
		if (gameMode === "online" || gameMode === "onlineTournament")
			ws.send(JSON.stringify({"type": "setting_change", "value": this.value}));
		else
			speedSliderValBelow.textContent = this.value / 10;
	}

	chatInput.focus();
}
