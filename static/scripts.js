let playAudio = function (trackId) {
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

let loadPlot = function (animate) {
    console.log('Loading plot');

    let embeddingsType = $('input[name="embeddings-type"]:checked').val();
    let nTracks = $('#n-tracks').val();
    let projectionType = $('input[name="projection-type"]:checked').val();
    if (projectionType === 'custom') {
        projectionType += '/' + $('#dim-x').val() + '/' + $('#dim-y').val();
    }

    console.log('Calling ajax...');
    $.ajax({
        url: '/plot/averages/' + embeddingsType + '/' + nTracks + '/' + projectionType,
        type: 'GET',
        contentType: 'application/json;charset=UTF-8',
        dataType: 'json',
        success: function (data) {
            console.log('Got plot data:');
            console.dir(data);
            if (animate) {
                Plotly.animate('plot', data, {xaxis: {autorange: true}, yaxis: {autorange: true}});
            } else {
                Plotly.newPlot('plot', data);
                $('#plot')[0].on('plotly_click', function(data) {
                    console.log('Click event:');
                    console.dir(data);
                    let id = data.points[0].id;
                    playAudio(id);
                });
            }
        }
    });
};

$(function() {
    loadPlot(false);

    // hide and show custom projection controls
    $('input[name="projection-type"]').on('change', function () {
        $('#projection-controls')[0].hidden = !$('#projection-custom')[0].checked;
    });

    $('#controls').on('submit', function (event) {
        event.preventDefault();
        console.dir(event);
        loadPlot(true);
    });
});