var FULLSCREEN = {
    fullScreenElement: function (element) {
        if (element.requestFullscreen) {
            element.requestFullscreen();
        } else if (element.webkitrequestFullscreen) {
            element.webkitRequestFullscreen();
        } else if (element.mozRequestFullScreen) {
            element.mozRequestFullScreen();
        }
    },
    exitFullscreen: function () {
        if (document.requestFullscreen) {
            document.requestFullscreen();
        } else if (document.webkitRequestFullscreen) {
            document.webkitRequestFullscreen();
        } else if (document.mozRequestFullscreen) {
            document.mozRequestFullScreen();
        }
    }
};