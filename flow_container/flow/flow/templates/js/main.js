const changeContainerContent = async (container, contentUrl) => {
    const response = await fetch('/content/' + contentUrl);
    const html = await response.text();
    container.replaceChildren(document.createRange().createContextualFragment(html));
}

const initPageLinks = () => {
    const pageLinks = document.getElementsByClassName('page_link');
    
    for (let i = 0; i < pageLinks.length; i++) {
        pageLinks[i].addEventListener('click',
            (event) => {
                event.preventDefault();
                changeContainerContent(document.body, pageLinks[i].getAttribute('href').substr(1));
            }
        );
    }
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
