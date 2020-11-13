let getJamendoMetadata = function (trackId, cb) {
    $.ajax({
        url: 'https://api.jamendo.com/v3.0/tracks/?client_id=98c98249&id=' + trackId.split(':')[0],  // TODO: move API key
        type: 'GET',
        dataType: 'json',
        success: function (data) {
            let trackData = data['results'][0];
            cb(trackData);
        }
    });
};

let playAudio = function (entityId) {
    let entity = current('data-type') === 'averages' ? 'track' : 'segment';
    $.ajax({
        url: '/audio/' + entity + '/' + entityId,
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

            let infoDiv = $('#track-info');
            infoDiv.html(data.text)
            // TODO: only when id changes, and maybe cache
            // getJamendoMetadata(entityId, function (data) {
            //     let infoDiv = $('#track-info');
            //     if (data) {
            //         infoDiv.html(data['artist_name'] + ' - ' + data['name'] +
            //             '&nbsp;<a href="https://jamen.do/t/' + data['id'] +
            //             '" target="_blank"><i class="fas fa-link"></i></a>');
            //     } else {
            //         infoDiv.html('');
            //     }
            // });
        }
    });
};

let stopAudio = function () {
    let audio = $('#audio')[0];
    audio.pause();
};


// TODO: replace as many calls to current as possible with parameter passing
// return the current value of the selector
let current = function (name) {
    return $('input[name=' + name + ']:checked').val();
};

// let selectingTags = function () {
//     return (current('layer') === 'taggrams') && (current('projection') === 'original');
// };


let getErrorMessage = function (status) {
    if (status >= 500) {
        return 'Something broke on the server';
    } if (status === 404) {
        return 'Data not available';
    } if (status === 400) {
        return 'Invalid data was sent to server';
    }
    return 'Something went wrong (' + status + ')';
};

let loadPlot = function (animate) {
    console.log('Loading plot');

    // TODO: replace this with form submit
    let nTracks = $('#n-tracks').val();
    let dataType = current('data-type');
    let dataset = current('dataset');
    let architecture = current('architecture');
    let layer = current('layer');
    let projection = current('projection');
    let dims = getCurrentDims(layer, projection);
    if (!dims) {
        bootbox.alert({
            message: 'Please select 2 dimensions',
            backdrop: true,
            centerVertical: true,
            size: 'small'
        });
        return;
    }

    let refreshButton = $('#btn-refresh');
    let refreshButtonSpinner = $('#btn-refresh-spinner');

    console.log('Calling ajax...');
    refreshButton.addClass('disabled');
    refreshButtonSpinner.show();

    $.ajax({
        type: 'GET',
        url: '/plot/' + dataType + '/' + dataset + '/' + architecture + '/' + layer + '/' + nTracks + '/' + projection + '/' + dims[0] + "/" + dims[1],
        dataType: 'json',
        success: function (data) {
            console.log('Got plot data:');
            console.dir(data);
            refreshButton.removeClass('disabled');
            refreshButtonSpinner.hide();

            localStorage.setItem('n-tracks', nTracks);
            localStorage.setItem('data-type', dataType);
            localStorage.setItem('architecture', architecture);
            localStorage.setItem('dataset', dataset);
            localStorage.setItem('layer', layer);
            localStorage.setItem('projection', projection);
            saveDims(dims);

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
            console.log('Error ' + data.status);
            if (data.status < 500) {
                console.dir(data.responseJSON.error);
            }
            bootbox.alert({
                title: "Error",
                message: getErrorMessage(data.status),
                backdrop: true,
                centerVertical: true,
                size: 'small'
            });

            refreshButton.removeClass('disabled');
            refreshButtonSpinner.hide();
        }
    });
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
    elementDropdown.selectpicker('val', getSavedDims());
};


let updateNumbers = function (elementNumbers, max) {
    let savedDims = getSavedDims();
    ['x', 'y'].forEach(function (axis, i) {
        $('#dim-'+axis).attr('max', max).attr('data-original-title',
            'embeddings layer index for ' + axis + '-axis (0~' + max + ')').val(savedDims[i]);
    });
    elementNumbers.show();
};


let getSavedDims = function () {
    let dimensions = JSON.parse(localStorage.getItem('dimensions'));
    return dimensions[current('architecture')][current('dataset')][current('layer')][current('projection')]
};

let saveDims = function (dimensions) {
    let savedDimensions = JSON.parse(localStorage.getItem('dimensions'));
    savedDimensions[current('architecture')][current('dataset')][current('layer')][current('projection')] = dimensions;
    localStorage.setItem('dimensions', JSON.stringify(savedDimensions))
}

let updateDimSelector = function (metadata) {
    let currentProjection = current('projection');
    let currentLayer = current('layer');

    let elementDropdown = $('#selector-dropdown');
    let elementNumbers = $('#selector-numbers');

    elementDropdown.selectpicker('hide');
    elementNumbers.hide();

    if (currentProjection === 'original') {
        if (currentLayer === 'taggrams') {
            updateDropdown(elementDropdown, function () {
                let tags = metadata['datasets'][current('dataset')]['tags'];
                tags.forEach(function (tag, i) {
                    elementDropdown.append('<option value="' + i + '" data-subtext="' + i + '">' + tag + '</option>');
                });
            });
        } else if (currentLayer === 'embeddings') {
            let currentArchitecture = current('architecture')
            updateNumbers(elementNumbers, metadata['architectures'][currentArchitecture]['embeddings'] - 1)
        }
    } else if (currentProjection === 'pca' || currentProjection === 'std-pca') {
        updateDropdown(elementDropdown, function () {
            for (let i=0; i < 6; i++) {  // TODO: get PCA percentages from server
                elementDropdown.append('<option value="' + i + '">PC' + (i+1) + '</option>');
            }
        });
    }
};

let getCurrentDims = function (layer, projection) {
    if (projection === 'tsne') {
        return [0, 1]
    }
    if (layer === 'embeddings' && projection === 'original') {
        return [$('#dim-x').val(), $('#dim-y').val()]
    }
    let dims = $('#selector-dropdown').val().map((x) => parseInt(x));
    if (dims.length === 2) {
        return dims
    }
    return false;
}

let initSelector = function (name, defaultValue, set = false) {
    let value = localStorage.getItem(name);
    value = value || defaultValue;
    $('#' + name + '-' + value).parent().button('toggle');
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

let initDims = function (metadata, defaultValue) {
    let dimensions = localStorage.getItem('dimensions');
    dimensions = JSON.parse(dimensions) || {}
    // TODO: make it better? cascade of fors looks horible.. maybe add semantics
    for (const architecture in metadata['architectures']) {
        dimensions[architecture] = dimensions[architecture] || {}
        for (const dataset of metadata['architectures'][architecture]['datasets']) {
            dimensions[architecture][dataset] = dimensions[architecture][dataset] || {};
            for (const layer in metadata['architectures'][architecture]['layers']) {
                dimensions[architecture][dataset][layer] = dimensions[architecture][dataset][layer] || {};
                for (const projection of ['original', 'pca']) {
                    dimensions[architecture][dataset][layer][projection] = dimensions[architecture][dataset][layer][projection] || defaultValue;
                }
            }
        }
    }
    localStorage.setItem('dimensions', JSON.stringify(dimensions));
}

$(function () {
    // init Bootstrap/Popper tooltips
    $('[data-toggle="tooltip"]').tooltip();

    // make sure that proper options are disabled dynamically
    getMetadata(function (metadata) {
        // TODO: save selections in the hierarchical way?

        for (const architecture in metadata['architectures']) {
            $('#architecture-' + architecture).change(function () {
                let datasets = metadata['architectures'][architecture]['datasets']
                updateSelectors('dataset', datasets, Object.keys(metadata['datasets']))

                let layers = Object.keys(metadata['architectures'][architecture]['layers'])
                updateSelectors('layer', layers, ['embeddings', 'taggrams'])

                updateDimSelector(metadata);
            });
        }

        let func = function () {
            updateDimSelector(metadata);
        };

        $('input[name=dataset]').change(func);
        $('input[name=layer]').change(func);
        $('input[name=projection]').change(func);

        initInput('n-tracks', 10);
        initSelector('data-type', 'segments');

        initDims(metadata, [0, 1])

        initSelector('architecture', 'musicnn');
        initSelector('dataset', 'mtt');
        initSelector('layer', 'taggrams');
        initSelector('projection', 'original');

        loadPlot(false);
    });

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

    // log-scale interaction
    $('#scale-log').click(function (e) {
        if (e.target.tagName.toUpperCase() === "LABEL") {
            return;
        }
        let type = this.checked ? 'log' : 'linear';
        let plotDiv = $('#plot')[0];
        let layout = plotDiv.layout;
        layout['xaxis']['type'] = type;
        layout['yaxis']['type'] = type;
        Plotly.relayout(plotDiv, layout);
    });

});