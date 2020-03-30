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

let getTags = function (cb) {
    $.ajax({
        url: '/tags',
        type: 'GET',
        contentType: 'application/json;charset=UTF-8',
        dataType: 'json',
        success: function (data) {
            console.log('Got tags');
            cb(data);
        }
    });
};

let stopAudio = function () {
    let audio = $('#audio')[0];
    audio.pause();
};

let currentSelectorValue = function (name) {
    return $('input[name='+name+']:checked').val();
};

let selectingTags = function () {
    return (currentSelectorValue('embeddings-type') === 'taggrams') && (currentSelectorValue('projection-type') === 'original');
};

let loadPlot = function (animate) {
    console.log('Loading plot');

    let nTracks = $('#n-tracks').val();
    let dataType = currentSelectorValue('data-type');
    let embeddingsType = currentSelectorValue('embeddings-type');
    let projectionType = currentSelectorValue('projection-type');
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
                // plotDiv.on('plotly_unhover', function(data) {
                //     console.log('Unhover event');
                //     stopAudio();
                // });
            }
            console.log('Assigning initial audio bind');
            changeAudioBind(localStorage.getItem('audio'), true);
        },
        error: function (data) {
            let error = data.responseJSON.error;
            console.log('Error: ' + error);
            alert(error);
        }
    });
};


let initSelector = function (name, defaultValue, set=false) {
    let value = localStorage.getItem(name);
    value = value || defaultValue;
    $('input[name="' + name + '"][value="' + value + '"]').closest('.btn').button('toggle');
    if (set) {
        localStorage.setItem(name, value)
    }
    return value
};


let initInput = function (id, defaultValue) {
    let value = localStorage.getItem(id);
    value = value || defaultValue;
    $('#' + id).val(value);
};

let plotEventHandler = function (data) {
    console.dir(data);
    let id = data.points[0].id;
    playAudio(id);
};

let changeAudioBind = function (value, init) {
    let plotDiv = $('#plot')[0];

    if (!init) {
        console.log('Removing listeners');
        plotDiv.removeAllListeners('plotly_hover');
        plotDiv.removeAllListeners('plotly_click');
    }

    let event = null;
    if (value === 'on-hover') {
        event = 'plotly_hover';
    } else if (value === 'on-click') {
        event = 'plotly_click';
    }

    if (event != null) {
        plotDiv.on(event, plotEventHandler);
    }

    localStorage.setItem('audio', value)
};

const dimensionControlIds = ['#dim-x', '#dim-y'];

let setDimensionMax = function (embeddingsType) {
    let max = null;
    if (embeddingsType === 'penultimate') {
        max = 199;
    } else if (embeddingsType === 'taggrams') {
        max = 49;
    }
    console.log('Changing dimension max: ' + max);

    for (const id of dimensionControlIds) {
        $(id).attr('max', max)
    }
};

$(function() {
    initSelector('data-type', 'trajectories');
    let embeddingsType = initSelector('embeddings-type', 'penultimate');
    setDimensionMax(embeddingsType);
    initSelector('projection-type', 'pca');
    initInput('n-tracks', 10);
    initInput('dim-x', 0);
    initInput('dim-y', 1);

    loadPlot(false);

    // hide custom projection controls on tsne
    $('input[name="projection-type"]').change(function () {
         $('#projection-controls')[0].hidden = this.value === 'tsne';
    });


    // limit dimensions
    $('input[name="embeddings-type"]').change(function () {
        setDimensionMax(this.value)
    });

    // submit button bind
    $('#controls').on('submit', function (event) {
        event.preventDefault();
        console.dir(event);
        loadPlot(true);
    });

    // audio bind functionality
    initSelector('audio', 'on-hover', true);
    $('input[name=audio]').change(function () {
        console.log('Changing audio bind: ' + this.value);
        changeAudioBind(this.value, false)
    });

    // dimensions popup
    getTags(function (tags) {
        let getTooltip = function () {
            if (currentSelectorValue('projection-type') === 'pca')
                return '% of total (todo)';
            if (currentSelectorValue('projection-type') === 'original') {
                if (currentSelectorValue('embeddings-type') === 'taggrams')
                    return tags[this.value];
                if (currentSelectorValue('embedding-type' === 'penultimate'))
                    return 'not sure'
                return '?'
            }
            return '?'
        };
        for (const id of dimensionControlIds) {
            $(id).popover({
                placement: 'right',
                content: getTooltip,
                trigger: 'focus'
            });
            $(id).change(function () {
                $(this).popover('hide');
                $(this).popover('show');
            });
            // $(id).focusin(function () {
            //     if (selectingTags()) {
            //         $(this).popover({placement: 'right', content: tags[this.value]})
            //     }
            // });
            // $(id).focusout(function () {
            //     $(this).popover('hide')
            // });
        }
    });

});