const changeContainerContent = async (container, contentUrl) => {
    const response = await fetch('/content/' + contentUrl);
    const html = await response.text();
    container.replaceChildren(document.createRange().createContextualFragment(html));
}

const changeContainerLobby = async (container, gameUrl) => {
    const response = await fetch('/content/lobby' + '?gameUrl=' + gameUrl);
    const html = await response.text();
    container.replaceChildren(document.createRange().createContextualFragment(html));
}

const loadPageHash = () => {
    if (window.location.hash)
        changeContainerContent(document.body, window.location.hash.substr(1));
    else
        changeContainerContent(document.body, "landing");
}

function getCookie(name) {
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

const pingServer = () => {
    fetch('/api/ping', {
        method: 'POST',
        headers: {'X-CSRFToken': getCookie('csrftoken')}
    });
}

addEventListener("load", loadPageHash );
addEventListener("load", pingServer );
addEventListener("hashchange", loadPageHash );

const pingInterval = setInterval(pingServer, 55000);
