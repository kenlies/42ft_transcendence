from django.contrib.auth.models import User
import re

def validate_alias(alias):
	if not alias:
		return "Alias is required!"
	elif len(alias) < 4:
		return "Alias must be at least 4 characters long!"
	elif len(alias) > 15:
		return "Alias must be at most 15 characters long!"
	elif not re.match("^[a-zA-Z0-9]+$", alias):
		return "Alias must contain only alphanumeric characters!"
	return None

def validate_username(username):
    if not username:
        return "Username is required!"
    elif len(username) < 4:
        return "Username must be at least 4 characters long!"
    elif len(username) > 15:
        return "Username must be at most 15 characters long!"
    elif not re.match("^[a-zA-Z0-9]+$", username):
        return "Username must contain only alphanumeric characters!"
    elif User.objects.filter(username=username).exists():
        return "Username already exists"
    return None

def validate_email(email):
    if not email:
        return "Email is required!"
    elif not re.match("^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$", email):
        return "Email is invalid!"
    return None

def validate_password(password, confirmPassword):
    if not password:
        return "Password is required!"
    elif len(password) < 5:
        return "Password must be at least 5 characters long!"
    elif len(password) > 20:
        return "Password must be at most 20 characters long!"
    elif not re.search("[A-Z]", password):
        return "Password must contain at least one upper-case letter!"
    elif not re.search("[a-z]", password):
        return "Password must contain at least one lower-case letter!"
    elif not re.search("[0-9]", password):
        return "Password must contain at least one digit character!"
    elif password != confirmPassword:
        return "Passwords do not match!"
    return None

def validate(data):
    if 'username' in data:
        error = validate_username(data['username'])
        if error:
            return error
    if 'email' in data:
        error = validate_email(data['email'])
        if error:
            return error
    if 'password' in data and 'confirm_password' in data:
        error = validate_password(data['password'], data['confirm_password'])
        if error:
            return error
    if 'password' in data and 'confirm_password' not in data:
        return "Confirm Password is required!"
    return None
