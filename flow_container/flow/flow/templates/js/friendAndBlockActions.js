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
        }
        else {
            addFriendError.innerHTML = result;
            addFriendError.classList.add("show");
        }
    }
    catch (error) {
        addFriendError.innerHTML = error;
        addFriendError.classList.add("show");
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
        }
        else {
            blockUserError.innerHTML = result;
            blockUserError.classList.add("show");
        }
    }
    catch (error) {
        blockUserError.innerHTML = error;
        blockUserError.classList.add("show");
    }
}
