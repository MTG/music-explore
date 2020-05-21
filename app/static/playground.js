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

let stopAudio = function () {
    let audio = $('#audio')[0];
    audio.pause();
};


// return the current value of the selector
let current = function (name) {
    return $('input[name=' + name + ']:checked').val();
};

// let selectingTags = function () {
//     return (current('layer') === 'taggrams') && (current('projection-type') === 'original');
// };


let loadPlot = function (animate) {
    console.log('Loading plot');

    // TODO: replace this with form submit
    let nTracks = $('#n-tracks').val();
    let dataType = current('data-type');
    let dataset = current('dataset');
    let model = current('model');
    let layer = current('layer');
    let projectionType = current('projection-type');
    let dimX = $('#dim-x').val();
    let dimY = $('#dim-y').val();

    let refreshButton = $('#btn-refresh');
    let refreshButtonSpinner = $('#btn-refresh-spinner');

    console.log('Calling ajax...');
    refreshButton.addClass('disabled');
    refreshButtonSpinner.show();

    $.ajax({
        type: 'GET',
        url: '/plot/' + dataType + '/' + dataset + '/' + model + '/' + layer + '/' + nTracks + '/' + projectionType + '/' + dimX + "/" + dimY,
        dataType: 'json',
        success: function (data) {
            console.log('Got plot data:');
            console.dir(data);
            refreshButton.removeClass('disabled');
            refreshButtonSpinner.hide();

            localStorage.setItem('data-type', dataType);
            localStorage.setItem('dataset', dataset);
            localStorage.setItem('model', model);
            localStorage.setItem('layer', layer);
            localStorage.setItem('n-tracks', nTracks);
            localStorage.setItem('projection-type', projectionType);
            localStorage.setItem('dim-x', dimX);
            localStorage.setItem('dim-y', dimY);

            // TODO: set animate appropriately
            animate = false;

            if (animate) {
                Plotly.animate('plot', data, {xaxis: {autorange: true}, yaxis: {autorange: true}});
            } else {
                Plotly.newPlot('plot', data, {}, {responsive: true});
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

            refreshButton.removeClass('disabled');
            refreshButtonSpinner.hide();
        }
    });
};


let initSelector = function (name, defaultValue, set = false) {
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
    if (value === 'hover') {
        event = 'plotly_hover';
    } else if (value === 'click') {
        event = 'plotly_click';
    }

    if (event != null) {
        plotDiv.on(event, plotEventHandler);
    }

    localStorage.setItem('audio', value)
};

let getMetadata = function (cb) {
    $.ajax({
        url: '/metadata',
        type: 'GET',
        contentType: 'application/json;charset=UTF-8',
        dataType: 'json',
        success: function (data) {
            console.log('Got metadata');
            cb(data);
        }
    });
};

// either disable or enable selector
let updateSelector = function (element, show=true, other) {
    if (element.prop('disabled') && show) {
        element.prop('disabled', false).parent().removeClass('disabled');
    } else if (!element.prop('disabled') && !show) {  // disable
        if (element.prop('checked')) {
            other.parent().button('toggle');
        }
        element.prop('disabled', true).parent().addClass('disabled');
    }
};

let updateSelectors = function (name, modelEntities, allEntities) {
    let firstElement = null;

    for (const entity of modelEntities) {
        let element = $('#' + name + '-' + entity);
        updateSelector(element, true);
        firstElement = firstElement || element;
    }
    for (const entity of allEntities) {
        if (!(modelEntities.includes(entity))) {
            updateSelector($('#' + name + '-' + entity), false, firstElement);
        }
    }
};


let updateDropdown = function (elementDropdown, populate) {
    elementDropdown.empty();
    elementDropdown.prop('title', 'Tags')
    populate();
    elementDropdown.selectpicker('refresh');
    elementDropdown.selectpicker('show');
};


let updateNumbers = function (elementNumbers, max) {
    console.log('Changing dimension max: ' + max);
    for (const i of ['x', 'y']) {
        $('#dim-'+i).attr('max', max).attr('data-original-title', 'Penultimate layer index for ' + i + '-axis');
    }
    elementNumbers.show();
};


let updateDimSelector = function (metadata) {
    let currentProjectionType = current('projection-type');
    let currentLayer = current('layer');

    let elementDropdown = $('#selector-dropdown');
    let elementNumbers = $('#selector-numbers');

    elementDropdown.selectpicker('hide');
    elementNumbers.hide();

    if (currentProjectionType === 'original') {
        if (currentLayer === 'taggrams') {
            updateDropdown(elementDropdown, function () {
                let tags = metadata['datasets'][current('dataset')]['tags'];
                tags.forEach(function (tag, i) {
                    elementDropdown.append('<option value="' + i + '" data-subtext="' + i + '">' + tag + '</option>');
                });
            });
        } else if (currentLayer === 'penultimate') {
            let currentModel = current('model')
            updateNumbers(elementNumbers, metadata['models'][currentModel]['penultimate'] - 1)
        }
    } else if (currentProjectionType === 'pca') {
        updateDropdown(elementDropdown, function () {
            for (let i=0; i < 6; i++) {  // TODO: get PCA percentages from server
                elementDropdown.append('<option value="' + i + '">PC' + (i+1) + '</option>');
            }
        });
    }
};

$(function () {
    // init Bootstrap/Popper tooltips
    $('[data-toggle="tooltip"]').tooltip();

    initSelector('data-type', 'segments');

    // make sure that proper options are disabled dynamically
    getMetadata(function (metadata) {
        // TODO: save selections in the hierarchical way?

        for (const model in metadata['models']) {
            $('#model-' + model).change(function () {
                let modelDatasets = metadata['models'][model]['datasets']
                updateSelectors('dataset', modelDatasets, Object.keys(metadata['datasets']))

                let modelLayers = metadata['models'][model]['layers']
                updateSelectors('layer', modelLayers, ['penultimate', 'taggrams'])

                // updateDimSelector(metadata); TODO: later to pudate PCA percentages
            });
        }
        initSelector('model', 'musicnn');

        let func = function () {
            updateDimSelector(metadata);
        };

        $('input[name=dataset]').change(func);
        $('input[name=layer]').change(func);
        $('input[name=projection-type]').change(func);


        initSelector('dataset', 'mtt');
        initSelector('layer', 'penultimate');
    });

    // setDimensionMax(layer);
    initSelector('projection-type', 'pca');
    initInput('n-tracks', 10);
    initInput('dim-x', 0);
    initInput('dim-y', 1);

    loadPlot(false);

    // // hide custom projection controls on tsne
    // $('input[name="projection-type"]').change(function () {
    //     $('#projection-controls')[0].hidden = this.value === 'tsne';
    // });


    // submit button bind
    $('#controls').on('submit', function (event) {
        event.preventDefault();
        console.dir(event);
        loadPlot(true);
    });

    // audio bind functionality
    initSelector('audio', 'hover', true);
    $('input[name=audio]').change(function () {
        console.log('Changing audio bind: ' + this.value);
        changeAudioBind(this.value, false)
    });

    $('#scale-log').click(function (e) {
        if (e.target.tagName.toUpperCase() === "LABEL") {
            return;
        }
        let type = this.checked ? 'log' : 'linear';
        let plotDiv = $('#plot')[0];
        Plotly.relayout(plotDiv, {
            xaxis: {
                type: type,
                autorange: true
            },
            yaxis: {
                type: type,
                autorange: true
            }
        });
        // TODO: keep labels
    });
});