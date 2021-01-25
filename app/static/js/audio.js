let playAudio = function (entity) {
    const audio = document.getElementById('audio');
    const infoDiv = document.getElementById('track-info');

    const xhr = createXhr('GET', `/audio/${entity}`);
    xhr.addEventListener('load', function (event) {
        console.log('Got audio url:');
        console.dir(this);
        audio.src = this.response.url;
        audio.load();
        audio.play();
        infoDiv.innerHTML = this.response.text;
    });
    xhr.send();
};


let bindAudio = function (plotId, eventType, clear) {
    const plotDiv = document.getElementById(plotId);

    if (clear) { // TODO: redo it to only remove the audio listener
        console.log('Removing listeners');
        plotDiv.removeAllListeners('plotly_hover');
        plotDiv.removeAllListeners('plotly_click');
    }

    let event = null;
    if (eventType === 'hover') {
        event = 'plotly_hover';
    } else if (eventType === 'click') {
        event = 'plotly_click';
    }

    if (event != null) {
        plotDiv.on(event, (event) => {
            let id = event.points[0].id;
            playAudio(id);
        });
    }
};
