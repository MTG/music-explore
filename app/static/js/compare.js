let getFormData = function (formId) {
    const form = document.getElementById(formId);
    const formData = new FormData(form);
    let result = {};
    for (const key of formData.keys()) {
        const values = formData.getAll(key);
        result[key] = values.length === 1 ? values[0] : values;
        console.dir(formElement);
        console.dir();
    }
    console.log('dimensions ' + formData.getAll('dimensions'));

    return Object.fromEntries((new FormData(form)).entries());
};

let loadPlot = function (side, otherSide) {
    const model = new FormData(document.getElementById(`form-${side}`));
    const data = new FormData(document.getElementById('form-data'));

    const requestData = {
        model: {
            architecture: model.get('architecture'),
            dataset: model.get('dataset'),
            layer: model.get('layer'),
            projection: model.get('projection'),
            dimensions: model.getAll('dimensions'),
        },
        // Data
        filters: {
            tags: data.getAll('tags'),
            artists: data.getAll('artists')
        }
    };

    let request = createXhr('POST', '/plot-advanced');
    request.addEventListener('load', function () {
        const plotId = `plot-${side}`;
        Plotly.newPlot(plotId, this.response, {dragmode: 'select'}, {responsive: true});
        bindCoupledHover(plotId, `plot-${otherSide}`);
        bindCoupledSelect(plotId, `plot-${otherSide}`);
        bindAudio(plotId, localStorage.getItem('audio'));
    });
    request.send(JSON.stringify(requestData));
};

let bindSubmit = function (formId, sides) {
    document.getElementById(formId).addEventListener('submit', function (event) {
        event.preventDefault();
        for (const [side, otherSide] of Object.entries(sides)) {
            loadPlot(side, otherSide);
        }
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
        console.dir(event);
        let somethingSelected = false;
        for (const curve of plotDiv.data) {
            let curveOpacities = new Array(curve.ids.length).fill(0.2);
            for (const selectedPoint of curve.selectedpoints) {
                curveOpacities[selectedPoint] = 1;
                somethingSelected = true;
            }
            opacities.push(curveOpacities);
        }
        console.dir(opacities);
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

$(function () {
    // init Bootstrap/Popper tooltips
    $('[data-toggle="tooltip"]').tooltip();

    bindSubmit('form-left', {'left': 'right'});
    bindSubmit('form-right', {'right': 'left'});
    bindSubmit('form-data', {'left': 'right', 'right': 'left'});

    bindTagSelector('form-left');
    bindTagSelector('form-right');

    document.getElementById('audio').volume = 0.5;
});
