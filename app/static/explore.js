let resetToStart = function (audio) {
    audio.currentTime = audio.src.split('=')[1].split(',')[0];
};

let bindPlayButtons = function () {
    let audio = $('audio')[0];
    $('.btn-play').click(function () {
        audio.src = this.getAttribute('audio-url');
        audio.load();
        audio.play();
    });
};

let bindLikeButtons = function () {
     
};

$(function () {
    bindPlayButtons();
});
