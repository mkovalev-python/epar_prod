/**
 * Created with PyCharm.
 * User: Gvammer
 * Date: 25.03.13
 * Time: 13:07
 */
var FancyWebSocket = function (url, obj) {
    var conn = new WebSocket(url);
    var callbacks = {};

    this.getCallBacks = function() {
        return callbacks;
    };

    this.rebindAll = function(cb) {
        var i, j;

        for (i in cb) {
            for (j in cb[i])
                (function(k, v, t) {t.bind(k, v)})(i, cb[i][j], this);
        }
    };

    this.bind = function (event_name, callback) {
        callbacks[event_name] = callbacks[event_name] || [];
        callbacks[event_name].push(callback);
        return this;
    };

    this.state = function() {
        return conn.readyState;
    };

    this.send = function (event_name, event_data) {
        var payload = JSON.stringify({event: event_name, data: event_data});
        conn.send(payload);
        return this;
    };

    // dispatch to the right handlers
    conn.onmessage = function (evt) {
        var json = JSON.parse(evt.data);
        dispatch(json.event, json.data);
    };

    conn.onclose = function () {
        dispatch('close', null)
    };
    conn.onopen = function () {
        dispatch('open', null)
    };

    var dispatch = function (event_name, message) {
        var chain = callbacks[event_name];
        if (typeof chain == 'undefined') return;
        for (var i = 0; i < chain.length; i++) {
            chain[i].call(obj, message)
        }
    }
};

var baseConnectorClass = function (data) {
    this.socket = false;
    this.url = data.url;
    this.connected = false;
    this.events = {};
    this.init();
};
baseConnectorClass.prototype = {
    'init': function () {
        var t = this;
        var port = document.location.protocol == 'https:' ? 'wss://' : 'ws://';
        var cb;
        if (this.socket) {
            cb = this.socket.getCallBacks();
        }
        this.socket = new FancyWebSocket((port + this.url), this);


        if (cb) {
            this.socket.rebindAll(cb);
        } else {
            this.addListener('connect', function () {
                t.connected = true;

                this.send('connect', {
                    sessionid: $.cookie("sessionid")
                });

                if (!window.timerID) {
                    window.timerID = setInterval(function () {
                        if (t.socket.state() == 3) {
                            t.init();
                            t.socket.rebindAll();
                        }
                    }, 8000);
                }
            });
        }
    },
    'disableAllInputs': function() {
        $('input, textarea, button').addClass('disabled js-disabled').attr('disabled', 'disabled');
    },
    'enableDisabledInputs': function() {
        $('.js-disabled').removeClass('disabled js-disabled').attr('disabled', false);
    },
    'addListener': function (event_name, func) {
        this.socket.bind(event_name, func);
    },
    'send': function (message, data, func) {
        this.socket.send(message, data);
        if (func) func();
    },
    'closeConnection': function () {
        this.socket.onclose = function () {
        };
        this.socket.close();
    }
};

var baseConnector = {};
$(function() {
    baseConnector = new baseConnectorClass({
        'url': (window.heliardSettings['SOCKET_SERVER_ADDRESS'] + ':8081')
    });
});