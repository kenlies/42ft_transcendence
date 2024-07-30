const changeContainerContent = async (container, contentUrl) => {
    const response = await fetch('/content/' + contentUrl);
    container.innerHTML = await response.text();
}
