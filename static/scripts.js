let load_plot = function() {
    console.log('Calling ajax...');
    $.ajax({
        url: '/plot',
        type: 'GET',
        contentType: 'application/json;charset=UTF-8',
        data: {},
        dataType: 'json',
        success: function (data) {
            console.log('Got data');
            console.dir(data);
            Plotly.newPlot('plot', data, {}, {responsive: true});
        }
    });
};


$(function() {
    console.log('Loading plot');
    load_plot();

    $('#plot').on('plotly_click', function(data) {
        console.dir(data.points);
    });
});