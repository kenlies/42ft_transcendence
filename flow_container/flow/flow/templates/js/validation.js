function validateUsername(username, errorField) {
    if (username.value === '' || username.value == null)
        errorField.innerHTML = "Username is required!";
    else if (username.value.length < 4)
        errorField.innerHTML = "Username must be at least 4 characters long!";
    else if (username.value.length > 15)
        errorField.innerHTML = "Username must be at most 15 characters long!";
    else if (!/^[a-zA-Z0-9]+$/.test(username.value))
        errorField.innerHTML = "Username must contain only alphanumeric characters!";
    else
        return true;
    username.classList.add('error');
    errorField.classList.add('show');
    return false;
}

function validateEmail(email, errorField) {
    if (email.value === '' || email.value == null)
        errorField.innerHTML = "Email is required!";
    else if (!/^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/.test(email.value))
        errorField.innerHTML = "Email is invalid!";
    else
        return true;
    email.classList.add('error');
    errorField.classList.add('show');
    return false;
}

function validatePassword(password, confirmPassword, errorField) {
    if (password.value === '' || password.value == null)
        errorField.innerHTML = "Password is required!";
    else if (password.value.length < 5)
        errorField.innerHTML = "Password must be at least 5 characters long!";
    else if (password.value.length > 20)
        errorField.innerHTML = "Password must be at most 20 characters long!";
    else if (!/[A-Z]/.test(password.value))
        errorField.innerHTML = "Password must contain at least one upper-case letter!";
    else if (!/[a-z]/.test(password.value))
        errorField.innerHTML = "Password must contain at least one lower-case letter!";
    else if (!/[0-9]/.test(password.value))
        errorField.innerHTML = "Password must contain at least one digit character!";
    else if (password.value !== confirmPassword.value) {
        errorField.innerHTML = "Passwords do not match!";
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
        errorField.innerHTML = "Message must be at most 500 characters long!";
    else if (message.value.startsWith('GAME_INVITE='))
        message.value = message.value.substring(12);
    else
        return true;
    errorField.classList.add('show');
    return false;
}
