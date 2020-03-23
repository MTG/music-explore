let playAudio = function (trackId) {
    // let parts = trackId.split(':');
    // if (parts.length > 0) {
    //     trackId = parts[0];
    //     let start = parts[1];
    //     let end = parts[2];
    // }
    $.ajax({
        url: '/jamendo/' + trackId,
        type: 'GET',
        contentType: 'application/json;charset=UTF-8',
        dataType: 'json',
        success: function (data) {
            console.log('Got jamendo url:');
            console.dir(data);
            $('#audio-source')[0].src = data.url;
            let audio = $('#audio')[0];
            audio.load();
            audio.play();
        }
    });
};

let stopAudio = function () {
    let audio = $('#audio')[0];
    audio.pause();
};

let loadPlot = function (animate) {
    console.log('Loading plot');

    let dataType = $('input[name="data-type"]:checked').val();
    let embeddingsType = $('input[name="embeddings-type"]:checked').val();
    let nTracks = $('#n-tracks').val();
    let projectionType = $('input[name="projection-type"]:checked').val();
    let dimX = $('#dim-x').val();
    let dimY = $('#dim-y').val();

    let refreshButton = $('#btn-refresh');
    let refreshButtonSpinner = $('#btn-refresh-spinner');

    console.log('Calling ajax...');
    refreshButton.addClass('disabled');
    refreshButtonSpinner.show();

    $.ajax({
        url: '/plot/' + dataType + '/' + embeddingsType + '/' + nTracks + '/' + projectionType + '/' + dimX + "/" + dimY,
        type: 'GET',
        contentType: 'application/json;charset=UTF-8',
        dataType: 'json',
        success: function (data) {
            console.log('Got plot data:');
            console.dir(data);
            refreshButton.removeClass('disabled');
            refreshButtonSpinner.hide();

            localStorage.setItem('data-type', dataType);
            localStorage.setItem('embeddings-type', embeddingsType);
            localStorage.setItem('n-tracks', nTracks);
            localStorage.setItem('projection-type', projectionType);
            localStorage.setItem('dim-x', dimX);
            localStorage.setItem('dim-y', dimY);

            // TODO: set animate appropriately
            animate = false;

            if (animate) {
                Plotly.animate('plot', data, {xaxis: {autorange: true}, yaxis: {autorange: true}});
            } else {
                Plotly.newPlot('plot', data);
                let plotDiv = $('#plot')[0];
                plotDiv.on('plotly_hover', function(data) {
                    console.log('Hover event:');
                    console.dir(data);
                    let id = data.points[0].id;
                    playAudio(id);
                });
                // plotDiv.on('plotly_unhover', function(data) {
                //     console.log('Unhover event');
                //     stopAudio();
                // });
            }
        },
        error: function (data) {
            let error = data.responseJSON.error;
            console.log('Error: ' + error);
            alert(error);
        }
    });
};


let initSelector = function (name, defaultValue) {
    let value = localStorage.getItem(name);
    value = value || defaultValue;
    $('input[name="' + name + '"][value="' + value + '"]').closest('.btn').button('toggle');
};


let initInput = function (id, defaultValue) {
    let value = localStorage.getItem(id);
    value = value || defaultValue;
    $('#' + id).val(value);
};


$(function() {
    initSelector('data-type', 'trajectories');
    initSelector('embeddings-type', 'penultimate');
    initSelector('projection-type', 'pca');
    initInput('n-tracks', 10);
    initInput('dim-x', 0);
    initInput('dim-y', 1);

    loadPlot(false);

    // hide and show custom projection controls
    // $('input[name="projection-type"]').on('change', function () {
    //     $('#projection-controls')[0].hidden = !$('#projection-custom')[0].checked;
    // });

    $('#controls').on('submit', function (event) {
        event.preventDefault();
        console.dir(event);
        loadPlot(true);
    });
});