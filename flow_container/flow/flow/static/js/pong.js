const changeContainerContent = async (container, contentUrl) => {
    const response = await fetch('/content/' + contentUrl);
    container.innerHTML = await response.text();
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
