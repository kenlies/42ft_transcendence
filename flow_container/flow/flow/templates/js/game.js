class Game {
    constructor(canvas, startValues){
        this.canvas = canvas;
        this.canvasContext = canvas.getContext("2d");
        this.fgColor = window.getComputedStyle(document.documentElement).getPropertyValue('--fg-color');

        this.paddleThic = 10;
        this.paddleLen = startValues.paddleHeight;
        this.paddleSpeed = startValues.paddleSpeed;
        this.leftpaddleY = startValues.player1Paddle_y_top;
        this.rightpaddleY = startValues.player2Paddle_y_top;

        this.ballRadius = 10;
        this.ballX = startValues.ball_x;
        this.ballY = startValues.ball_y;
        this.ballSpeed = startValues.ballSpeed;

        this.ballSpeedX = startValues.ballDeltaX;
        this.ballSpeedY = startValues.ballDeltaY;
        this.ballDirectionX = 1;
        this.ballDirectionY = 1;

        this.goalsPlayer1 = startValues.goalsPlayer1;
        this.goalsPlayer2 = startValues.goalsPlayer2;

        this.player1 = startValues.player1_username;
        this.player2 = startValues.player2_username;

        this.pressedKeys = [];
    }

    updateValues(newValues){
        this.leftpaddleY = newValues.player1Paddle_y_top;
        this.rightpaddleY = newValues.player2Paddle_y_top;

        this.ballX = newValues.ball_x;
        this.ballY = newValues.ball_y;

        this.ballSpeedX = newValues.ballDeltaX;
        this.ballSpeedY = newValues.ballDeltaY;

        this.goalsPlayer1 = newValues.goalsPlayer1;
        this.goalsPlayer2 = newValues.goalsPlayer2;
    }

    keyPressEvent(event) {
        this.pressedKeys[event.keyCode] = true;
    }

    keyReleaseEvent(event) {
        this.pressedKeys[event.keyCode] = false;
    }

    initKeyEvents() {
        window.addEventListener('keydown', (e) => this.keyPressEvent(e), false);
        window.addEventListener('keyup', (e) => this.keyReleaseEvent(e), false);
    }

    drawBall() {
        this.canvasContext.fillStyle = this.fgColor;
        this.canvasContext.fillRect(
            this.ballX * (this.canvas.width - this.ballRadius * 2  - this.paddleThic * 2 ) + this.paddleThic,
            this.ballY * (this.canvas.height - this.ballRadius * 2),
            this.ballRadius * 2,
            this.ballRadius * 2);
    }

    drawLeftpaddle() {
        this.canvasContext.fillStyle = this.fgColor;
        this.canvasContext.fillRect(
            0,
            this.leftpaddleY * this.canvas.height + this.ballRadius,
            this.paddleThic,
            this.paddleLen * this.canvas.height - (this.ballRadius * 2));
    }

    drawRightpaddle() {
        this.canvasContext.fillStyle = this.fgColor;
        this.canvasContext.fillRect(
            this.canvas.width - this.paddleThic,
            this.rightpaddleY * this.canvas.height + this.ballRadius,
            this.paddleThic,
            this.paddleLen * this.canvas.height - (this.ballRadius * 2));
    }

    updatePaddlePosition() {
        if (this.pressedKeys[38] || this.pressedKeys[40] || this.pressedKeys[83] || this.pressedKeys[87]) {
            if (this.player1 === username) {
                // W or up
                if ((this.pressedKeys[87] || this.pressedKeys[38]) && this.leftpaddleY  > 0) {
                    this.leftpaddleY -= this.paddleSpeed / 10;
                }
                // S or down
                if ((this.pressedKeys[83] || this.pressedKeys[40]) && this.leftpaddleY  < 1.0 - this.paddleLen) {
                    this.leftpaddleY += this.paddleSpeed / 10;
                }
                ws.send(JSON.stringify({"type": "paddle_position", "value": this.leftpaddleY}));
            }
            else if (this.player2 === username) {
                // W or up
                if ((this.pressedKeys[87] || this.pressedKeys[38]) && this.rightpaddleY > 0) {
                    this.rightpaddleY -= this.paddleSpeed / 10;
                }
                // S or down
                if ((this.pressedKeys[83] || this.pressedKeys[40]) && this.rightpaddleY < 1.0 - this.paddleLen) {
                    this.rightpaddleY += this.paddleSpeed / 10;
                }
                ws.send(JSON.stringify({"type": "paddle_position", "value": this.rightpaddleY}));
            }
        }
    }

    draw() {
        this.updatePaddlePosition();
        this.canvasContext.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.drawLeftpaddle();
        this.drawRightpaddle();
        this.drawBall();
    }
}
