async function addFriend(friendUsername, addFriendError) {
    const token = getCookie('csrftoken');
    try {
        const response = await fetch('/api/friend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': token
            },
            body: JSON.stringify({
                friendUsername: friendUsername
            }),
        });

        const result = await response.text();

        if (response.ok) {
            console.log('Friend added.');
            return true;
        }
        else {
            addFriendError.textContent = result;
            addFriendError.classList.add("show");
            return false;
        }
    }
    catch (error) {
        addFriendError.textContent = error;
        addFriendError.classList.add("show");
        return false;
    }
}

async function blockUser(blockUsername, blockUserError) {
    const token = getCookie('csrftoken');
    try {
        const response = await fetch('/api/block', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': token
            },
            body: JSON.stringify({
                blockUsername: blockUsername
            }),
        });

        const result = await response.text();

        if (response.ok) {
            console.log('User blocked');
            return true;
        }
        else {
            blockUserError.textContent = result;
            blockUserError.classList.add("show");
            return false;
        }
    }
    catch (error) {
        blockUserError.textContent = error;
        blockUserError.classList.add("show");
        return false;
    }
}
