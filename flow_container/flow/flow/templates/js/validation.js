function validateUsername(username, errorField) {
    if (username.value === '' || username.value == null)
        errorField.textContent = "Username is required!";
    else if (username.value.length < 4)
        errorField.textContent = "Username must be at least 4 characters long!";
    else if (username.value.length > 15)
        errorField.textContent = "Username must be at most 15 characters long!";
    else if (!/^[a-zA-Z0-9]+$/.test(username.value))
        errorField.textContent = "Username must contain only alphanumeric characters!";
    else
        return true;
    username.classList.add('error');
    errorField.classList.add('show');
    return false;
}

function validateEmail(email, errorField) {
    if (email.value === '' || email.value == null)
        errorField.textContent = "Email is required!";
    else if (!/^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/.test(email.value))
        errorField.textContent = "Email is invalid!";
    else
        return true;
    email.classList.add('error');
    errorField.classList.add('show');
    return false;
}

function validatePassword(password, confirmPassword, errorField) {
    if (password.value === '' || password.value == null)
        errorField.textContent = "Password is required!";
    else if (password.value.length < 5)
        errorField.textContent = "Password must be at least 5 characters long!";
    else if (password.value.length > 20)
        errorField.textContent = "Password must be at most 20 characters long!";
    else if (!/[A-Z]/.test(password.value))
        errorField.textContent = "Password must contain at least one upper-case letter!";
    else if (!/[a-z]/.test(password.value))
        errorField.textContent = "Password must contain at least one lower-case letter!";
    else if (!/[0-9]/.test(password.value))
        errorField.textContent = "Password must contain at least one digit character!";
    else if (password.value !== confirmPassword.value) {
        errorField.textContent = "Passwords do not match!";
        confirmPassword.classList.add('error');
    }
    else
        return true;
    password.classList.add('error');
    errorField.classList.add('show');
    return false;
}

function validateChatMessage(message, errorField) {
    if (message.value === '' || message.value == null)
        return false;
    else if (/^\s*$/.test(message.value)) {
        message.value = '';
        return false;
    }
    else if (message.value.length > 500)
        errorField.textContent = "Message must be at most 500 characters long!";
    else if (message.value.startsWith('GAME_INVITE='))
        message.value = message.value.substring(12);
    else
        return true;
    errorField.classList.add('show');
    return false;
}
