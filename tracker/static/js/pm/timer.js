/**
 * Created by tracker_maker on 13.08.15.
 */
var PM_Timer = function (data) {
    if (typeof(data) == 'object' || typeof(data) == 'array') {
        if (data.seconds) this.seconds = data.seconds * 1; else this.seconds = 0;
        if (data.minutes) this.minutes = data.minutes * 1; else this.minutes = 0;
        if (data.hours) this.hours = data.hours * 1; else this.hours = 0;
        if (data.container) this.container = data.container;
        if (data.started) this.started = data.started;
    } else if (parseInt(data)) {
        this.seconds = parseInt(data);
        this.minutes = 0;
        this.hours = 0;
    } else {
        this.seconds = 0;
        this.minutes = 0;
        this.hours = 0;
    }

    this.init();
    if (this.started) {
        this.start();
    }
};

PM_Timer.prototype = {
    'init': function () {
        if (this.seconds > 60) {
            this.minutes += Math.floor(this.seconds / 60);
            this.seconds = this.seconds % 60;
        }
        if (this.minutes > 60) {
            this.hours += Math.floor(this.minutes / 60);
            this.minutes = this.minutes % 60;
        }
    },
    'start': function () {
        var obj = this;
        if (this.interval) clearInterval(this.interval);
        this.interval = setInterval(function () {
            obj.seconds++;
            obj.init();
            obj.fill();
        }, 1000);
        this.started = true;
    },
    'stop': function () {
        if (this.interval) clearInterval(this.interval);
        this.started = false;
    },
    'toString': function () {
        var hours = this.hours * 1 || 0,
            minutes = this.minutes * 1 || 0,
            seconds = this.seconds * 1 || 0;

        if (hours < 10 && (hours.length < 2 || hours.length == undefined)) hours = '0' + hours + '';
        if (minutes < 10 && (minutes.length < 2 || minutes.length == undefined)) minutes = '0' + minutes + '';
        if (seconds < 10 && (seconds.length < 2 || seconds.length == undefined)) seconds = '0' + seconds + '';

        return hours + ":" + minutes + ":" + seconds;
    },
    'fill': function(){
        if (this.container) {
            $(this.container).html(this.toString())
        }
    }
};
