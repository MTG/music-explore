const otherSide = {
    left: 'right',
    right: 'left'
};

let loadPlot = function (sides, ) {
    const data = new FormData(document.getElementById('form-data'));
    const highlight = new FormData(document.getElementById('form-highlight'));

    let requestData = {
        models: {},
        data: {
            tags: data.getAll('tags'),
            artists: data.getAll('artists'),
            sparse: data.get('sparse'),
            webgl: document.getElementById('check-webgl').checked
        }
    };

    let ids = [];
    for (const values of highlight.getAll('highlight-items')) {
        ids = ids.concat(JSON.parse(values))
    }
    requestData.highlight = [...new Set(ids)];  // TODO: read about ellipsis in JS

    for(const side of sides){
        const model = new FormData(document.getElementById(`form-${side}`));
        requestData.models[side] = {
            architecture: model.get('architecture'),
            dataset: model.get('dataset'),
            layer: model.get('layer'),
            projection: model.get('projection')
        }
    }

    let request = createXhr('POST', '/plot-advanced');
    request.addEventListener('load', function () {
        const response = this.response;
        console.dir(response);

        for(const side of sides) {  // not sure if better to use the sides, or iterate on returned result
            const plotId = `plot-${side}`;
            const otherPlotId = `plot-${otherSide[side]}`;

            let layout = response.plots[side].layout;
            layout['dragmode'] = 'lasso';
            Plotly.newPlot(plotId, response.plots[side].data, layout, {responsive: true});

            // TODO: only do bindings when there is equal total number of points in both graphs -> they are comparable
            bindCoupledHover(plotId, otherPlotId);
            bindCoupledSelect(plotId, otherPlotId);

            const form = new FormData(document.getElementById(`form-highlight`));
            bindAudio(plotId, form.get('play'));
        }

        bindHighlightData(response.highlight)
    });
    request.send(JSON.stringify(requestData));
};

let bindHighlightData = function (data) {
    const entityFilter = document.getElementById('highlight-entity');
    const itemsFilter = document.getElementById('highlight-items');
    entityFilter.addEventListener('change', function (event) {
        itemsFilter.options.length = 0;
        const entity = this.value;
        if (entity) {
            for (const [text, values] of Object.entries(data[entity])) {
                itemsFilter.add(new Option(text, JSON.stringify(values)));
            }
        }
        $(itemsFilter).selectpicker('refresh');  // necessary jquery, hopefully selectpicker will drop jquery
    })
}

let bindSubmit = function (formId, sides, cb) {
    document.getElementById(formId).addEventListener('submit', function (event) {
        event.preventDefault();
        if (cb) cb();  // optional code to execute before loading plot
        loadPlot(sides);
    });
};

let bindCoupledHover = function (src, dst) {
    const plotDiv = document.getElementById(src);
    plotDiv.on('plotly_hover', function (event) {
        const point = event.points[0],
            curveNumber = point.curveNumber,
            pointNumber = point.pointNumber;
        Plotly.Fx.hover(dst, [{curveNumber: curveNumber, pointNumber: pointNumber}]);
    });
    plotDiv.on('plotly_unhover', function (event) {
        Plotly.Fx.unhover(dst);
    });
};


let bindCoupledSelect = function (src, dst) {
    const plotDiv = document.getElementById(src);

    let selectHandler = function (event) {
        let opacities = [];
        // console.dir(event);
        let somethingSelected = false;
        for (const curve of plotDiv.data) {
            let curveOpacities = new Array(curve.ids.length).fill(0.2);
            for (const selectedPoint of curve.selectedpoints) {
                curveOpacities[selectedPoint] = 1;
                somethingSelected = true;
            }
            opacities.push(curveOpacities);
        }
        // console.dir(opacities);
        if (somethingSelected) {
            Plotly.restyle(dst, 'marker.opacity', opacities);
        } else {
            Plotly.restyle(dst, 'marker.opacity', 1);
        }
    };

    plotDiv.on('plotly_selected', function (event) {
        if (event) {
            selectHandler(event);
        }
    });
    plotDiv.on('plotly_deselect', function () {
        Plotly.restyle(dst, 'marker.opacity', 1);
    });
};

let getSelectedSegments = function (src) {
    const plotDiv = document.getElementById(src);

    let points = [];
    const somethingSelected = plotDiv.data[0].hasOwnProperty('selectedpoints');  // not liking it too much
    for (const curve of plotDiv.data) {
        const curvePoints = somethingSelected ? curve.selectedpoints.map(i => curve.ids[i]) : curve.ids;
        points = points.concat(curvePoints);
    }
    return points;
}

let bindTagSelector = function (formId) {
    const form = document.getElementById(formId);
    const dimensionSelectors = [
        form['dimension-x'],
        form['dimension-y']
    ];
    form.addEventListener('change', function (event) {
        console.log(form['layer'].value, form['projection'].value);
        if (form['projection'].value === 'original') {
            for (const dimensionSelector of dimensionSelectors) {
                dimensionSelector.parentElement.parentElement.style.display = 'block';
            }
        } else {
            for (const dimensionSelector of dimensionSelectors) {
                dimensionSelector.parentElement.parentElement.style.display = 'none';
            }
        }
    });
};

let bindFilters = function () {
    document.getElementsByName('filter-entity').forEach(function (element) {
        const itemsElement = this.parentNode.parentNode.querySelector('select[name=filter-items]')
        element.addEventListener('change', function (e) {
            itemsElement.options.length = 0
            itemsElement.options.appendChild(new Option(`Option for ${element.value}`))
        })
    });
        a.parentNode.parentNode.querySelector('select[name=filter-items]')

};

const bindPlaylistButton = function() {
    document.getElementById('btn-playlist').addEventListener('click', event => {
        event.preventDefault();
        const selectedSegments = Object.keys(otherSide).map(side => getSelectedSegments(`plot-${side}`));
        console.log(selectedSegments);
        // TODO: intersect
    });
}

$(function () {
    // init Bootstrap/Popper tooltips
    $('[data-toggle="tooltip"]').tooltip();

    bindSubmit('form-left', ['left']);
    bindSubmit('form-right', ['right']);
    bindSubmit('form-data', ['left', 'right'], function () {
        console.log('highlight reset');
        document.getElementById('highlight-entity').value = '';
        document.getElementById('highlight-items').options.length = 0;
        // necessary evil
        $('#highlight-entity').selectpicker('refresh');
        $('#highlight-items').selectpicker('refresh');
    });
    bindSubmit('form-highlight', ['left', 'right']);
    bindPlaylistButton();
    // bindTagSelector('form-left');
    // bindTagSelector('form-right');

    document.getElementById('audio').volume = 0.5;
});
