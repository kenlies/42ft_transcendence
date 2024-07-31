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
