let bindOptionsPlayAudio = function () {
    const elements = document.getElementsByName('segment-choice');
    const submitButton = document.getElementById('submit');
    for (const element of elements) {
        element.addEventListener('click', function () {
            if (this.value) {
                playAudio(this.value);
            }
            submitButton.disabled = false;
        });
    }
    document.getElementById('segment-reference').addEventListener('click', function () {
        playAudio(this.value);
    });
}

let bindSubmit = function () {
    document.getElementById('submit').addEventListener('click', function () {
        const selectedOption = document.querySelector('input[name=segment-choice]:checked');
        if (selectedOption) {
            const xhr = createXhr('POST', '/similarity-result');
            xhr.addEventListener('load', function () {
                console.dir(this.response);
                document.getElementById('results').style.display = 'block';
                // location.reload();
            });
            const choices = Array.from(document.getElementsByName('segment-choice'), x => x.value);
            const result = {
                'reference': document.getElementById('segment-reference').value,
                'choices': choices,
                'selected': selectedOption.value,
                'model': document.getElementById('model').innerHTML
            }
            console.log(result);
            const closestIdx = document.getElementById('closest-idx').innerHTML - 1
            console.log(choices[closestIdx], selectedOption.value)
            const alertId = (choices[closestIdx] === selectedOption.value) ? 'alert-match' : 'alert-mismatch'
            document.getElementById(alertId).style.display = 'block';

            xhr.send(JSON.stringify(result));
        }
    })
}

$(function () {
    // init Bootstrap/Popper tooltips
    $('[data-toggle="tooltip"]').tooltip();
    bindOptionsPlayAudio();
    bindSubmit();
    document.getElementById('audio').volume = 0.5;
});
