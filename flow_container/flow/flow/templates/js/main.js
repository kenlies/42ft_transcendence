const changeContainerContent = async (container, contentUrl) => {
    try {
        const response = await fetch('/content/' + contentUrl);
        const html = await response.text();

        if (response.ok) {
            container.replaceChildren(document.createRange().createContextualFragment(html));
        } else {
            container.textContent = 'Error fetching content: ' + html;
        }
    } catch (error) {
        container.textContent = 'Error fetching content: ' + error;
    }
}

const changeContainerLobby = async (container, gameUrl) => {
    const response = await fetch('/content/lobby' + '?gameUrl=' + gameUrl);
    const html = await response.text();
    container.replaceChildren(document.createRange().createContextualFragment(html));
}

const loadPageHash = () => {
    if (window.location.hash)
        changeContainerContent(document.body, window.location.hash.substr(1).replace('/', ''));
    else
        changeContainerContent(document.body, "landing");
}

const getCookie = (name) => {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const joinLobby = async (game_url) => {
    removeEventListener("hashchange", loadPageHash);
    addEventListener("hashchange", (event) => {
        changeContainerLobby(document.body, game_url);
        addEventListener("hashchange", loadPageHash);
    },
    { once: true });
    window.location.hash = 'lobby';
}

const pingServer = async () => {
    try {
        await fetch('/api/ping', {
            method: 'POST',
            headers: {'X-CSRFToken': getCookie('csrftoken')}
        });
    } catch (error) {
        console.log('Error pinging server: ' + error);
    }
}

addEventListener("load", loadPageHash );
addEventListener("load", pingServer );
addEventListener("hashchange", loadPageHash );

const pingInterval = setInterval(pingServer, 55000);
