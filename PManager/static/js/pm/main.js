/**
 * Created with PyCharm.
 * User: Gvammer
 * Date: 18.10.12
 * Time: 14:34
 */
(function ($) {
    window.historyManager = (function () {
        var history = $.history;
        var self = this;
        this.params = {};
        this.callbacks = [];
        this.url = '';

        var hasOwnProperty = Object.prototype.hasOwnProperty;

        function isEmpty(obj) {

            // null and undefined are "empty"
            if (obj == null) return true;

            // Assume if it has a length property with a non-zero value
            // that that property is correct.
            if (obj.length > 0)    return false;
            if (obj.length === 0)  return true;

            // Otherwise, does it have any properties of its own?
            // Note that this doesn't handle
            // toString and valueOf enumeration bugs in IE < 9
            for (var key in obj) {
                if (hasOwnProperty.call(obj, key)) return false;
            }

            return true;
        }

        this.trigger = function (event) {
            for (var k in self.callbacks) {
                if (self.callbacks[k]['name'] == event) {
                    self.parseUrl(self.url);
                    self.callbacks[k]['func'].call(self, self.params);
                }
            }
        };

        this.addParams = function (params) {
            this.params = $.extend(this.params, params);
            this.pushUrl();
            this.saveCookie(this.params);
        };

        this.saveCookie = function (params) {
            var arFilter;
            try {
                arFilter = $.parseJSON($.cookie('saved_task_filters') || '{}');
            } catch (e) {
                arFilter = {};
            }
            arFilter[window.currentProject] = params;
            $.cookie('saved_task_filters', JSON.stringify(arFilter));
        };

        this.getSavedFilter = function () {
            var arFilter;
            try {
                arFilter = $.parseJSON($.cookie('saved_task_filters') || '{}');
            } catch (e) {
                arFilter = {};
            }

            return arFilter[window.currentProject] || false;
        };

        this.addCallback = function (name, callback) {
            if (typeof name == 'function') {
                callback = name;
                name = false;
            }
            self.callbacks.push({'name': name, 'func': callback});
        };

        this.pushUrl = function () {
            history.push(encodeURIComponent(JSON.stringify(this.params)));
        };

        this.parseUrl = function (url) {
            if (url) {
                try {
                    this.params = $.parseJSON(decodeURIComponent(url));
                } catch(e) {

                }
            }

            if (isEmpty(this.params)) {
                this.params = this.getSavedFilter();

                if (this.params)
                    this.pushUrl();
            }

            if (isEmpty(this.params)) {
                this.params = {};
            }
        };

        history.on('load change', function (event, url, type) {
            if (url) {
                this.url = url;
                self.parseUrl(url);
                for (var k in self.callbacks) {
                    self.callbacks[k]['func'].call(self, self.params);
                }
            }
        });
        history.listen('hash');
        return this;
    })();
})(jQuery);

function closePopups() {
    $('.pup').hide();
}

function getKeyPressed(e) {
    var key;
    if (window.event) {
        key = window.event.keyCode;
    } else {
        key = e.keyCode;
    }
    return key;
}

try {
    jQuery.expr[":"].Contains = jQuery.expr.createPseudo(function (arg) {
        return function (elem) {
            return jQuery(elem).text().toUpperCase().indexOf(arg.toUpperCase()) >= 0;
        };
    });
} catch (e) {

}

$.fn.enterPressed = function (func) {
    this.unbind('keydown.enter').bind('keydown.enter', function (e) {
        var key = getKeyPressed(e);
        if (key == 13) func(this);
    });
    return this;
};

var widgetObject = function (widgetData) {
    this.id = widgetData.id;
    this.aReadyFunc = [];
    this.state = {

    };

    this.container = widgetData.container;
    if (widgetData.init && typeof widgetData.init == 'function')
        this.init = widgetData.init;
};

widgetObject.prototype = {
    init: function () {

    },
    'ready': function (callback) {
        if (callback) {
            this.aReadyFunc.push(callback);
        } else {
            for (var i in this.aReadyFunc) {
                this.aReadyFunc[i].call(this);
            }
        }
    }
};

var mainControllerClass = function (data) {
    this.userId = data.userId;
    this.isClient = data.isClient ? true : false;
    this.isEmployee = data.isEmployee ? true : false;
    this.isAdmin = data.isAdmin ? true : false;

    this.widgetsData = data.widgetsData;
    this.init();
};

mainControllerClass.prototype = {
    init: function () {

    },
    inviteUser: function($btn, $email, $roles) {
        var arEmail = [], roles = {};
        $email.each(function(){
            if ($(this).val()) {
                var t = this,
                    $roleChecks = $(this).closest('.js-invite-cont').find('[type=radio]');

                $roleChecks.filter(':checked').each(function(){
                    if (!roles[$(t).val()]) roles[$(t).val()] = [];
                    roles[$(t).val()].push($(this).val());
                });

                if (!roles[$(t).val()] || roles[$(t).val()].length <= 0) {
                    alert('Выберите хоть одну роль в проекте.');
                    return false;
                }

                arEmail.push($(this).val());
            }
        });

        if (arEmail.length <= 0) {
                alert('Введите корректный email');
                return false;
        } else {
            PM_AjaxPost(
                '/users_ajax/',
                {
                    'action': 'inviteUser',
                    'email': arEmail,
                    'roles': roles
                },
                function(data){
                    $email.val('');
                    if (data == 'ok') {
                        alert('Пользователи успешно приглашены!');
                    } else {
                        alert(data);
                    }
                }
            )
        }
    }
};

function formatDate(date) {
    var dd = date.getDate();
    var mm = date.getMonth() + 1;
    var yyyy = date.getFullYear();
    var hours = date.getHours();
    var minutes = date.getMinutes();
    if (dd < 10) {
        dd = '0' + dd;
    }
    if (mm < 10) {
        mm = '0' + mm;
    }
    var formatted = dd + '.' + mm + '.' + yyyy;
    if (typeof hours === 'number' && typeof minutes === 'number') {
        // hours and minutes can be 0
        if (hours < 10) {
            hours = '0' + hours;
        }
        if (minutes < 10) {
            minutes = '0' + minutes;
        }
        formatted += ' ' + hours + ':' + minutes;
    }
    return formatted;
}

function PM_AjaxPost(url, data, func, type) {
    if (!data.project) {
        if (window.currentProject)
            data.project = parseInt(window.currentProject);
        else
            data.project = 0;
    }
    return $.post(url, data, func, type);
}



/***
 *
 * @param name - may be "small
 * @param container
 * @param add_params
 */
function startLoader(name, container, add_params) {
    container = $(container);
    if (!container.is(":visible")) {
            return false;
    }
    $loader = $('.loader.' + name + '');
    var objPos = getObjectCenterPos(container);

    if (!add_params) add_params = {"left": 0, "top": 0}
    if (!add_params.left) add_params.left = 0;
    if (!add_params.top) add_params.top = 0;

    if (add_params.modal) {
        return $loader.css({
            position: 'fixed',
            left: '50%',
            top: '50%'
        }).show();
    }
    if (add_params.exception) {
        $loader.addClass('dont_hide');
    } else {
        $loader.removeClass("dont_hide");
    }
    var w_h = parseInt($loader.width());
    return $loader.css({
        'position': 'absolute',
        'left': (objPos.left + (objPos.width / 2) + add_params.left - w_h / 2),
        'top': (objPos.top + (objPos.height / 2) + add_params.top - w_h / 2)
    }).show();
}

function stopLoader(objloader) {
    if (objloader && typeof(objloader.hide) == 'function')
        objloader.hide();
}

function stopLoaders() {
    $('.loader').hide();
}

function getObjectCenterPos(container) {
    if (typeof(container) == 'object') {
        container = $(container);
        if (!container.is(":visible")) {
            return false;
        }
    }
    var heightObj = 0;
    var widthObj = 0;
    var offset = {};
    if (container && container != "") {
        $container = $(container);
        offset = $container.offset();
        var cont = $container.get(0);
        if (cont) {
            heightObj = cont.offsetHeight;
            widthObj = cont.offsetWidth;
        }
    }
    var ret = {left: offset.left, top: offset.top, width: widthObj, height: heightObj}
    return ret;
}

$(function () {
    $('.optionRowPopUp, .widgets-list').bind("clickoutside", function () {
        $(this).hide();
    });

    $('input[data-blur],textarea[data-blur]').focus(function () {
        if ($(this).val() == $(this).attr('data-blur')) {
            $(this).val('');
        }
    }).blur(function () {
            if ($(this).val() == '') {
                $(this).val($(this).attr('data-blur'));
            }
        });

    $(document).on('click', 'a', function () {
        closePopups();
    });
});

function showOverlay() {
    $('.overlay').show();
}
function hideOverlay() {
    $('.overlay').hide();
}

$.fn.pushed = function () {
    return this.hasClass('activated');
};
$.fn.pushTheButton = function () {
    this.data(
        'loader',
        startLoader('small', this.get(0))
    );
    this.addClass('activated');
    return this;
};
$.fn.pullTheButton = function () {
    stopLoader(this.data('loader'));
    this.removeClass('activated');
    return this;
};
$.fn.hasAttr = function (name) {
    return this.attr(name) !== undefined;
};

$.fn.selectText = function () {
    var range, selection;
    return this.each(function () {
        if (document.body.createTextRange) {
            range = document.body.createTextRange();
            range.moveToElementText(this);
            range.select();
        } else if (window.getSelection) {
            selection = window.getSelection();
            range = document.createRange();
            range.selectNodeContents(this);
            selection.removeAllRanges();
            selection.addRange(range);
        }
    });
    return this;
};

$.fn.setEditable = function (callback) {
    var t = this;
    setTimeout(function () {
        t.attr('contenteditable', true).focus().selectText();
        $(document).unbind('mouseup.editableContent').one('mouseup.editableContent', function () {
            $(t).attr('contenteditable', false).trigger('blur');
            callback.call(t);
        });
        t.enterPressed(function () {
            $(t).attr('contenteditable', false).trigger('blur');
            callback.call(t);
        });
    }, 100);
};

$.fn.activateListItem = function(){
    this.addClass('active').siblings().removeClass('active');
    return this;
};

var bLinkEscape;
$(function () {
    $(document).on('mousedown', 'a[href]', function () {
        bLinkEscape = true;
    });
    $('.js-main-fnc').fancybox({
        'type': 'ajax'
    });
});

window.onbeforeunload = function (evt) {
    if (!bLinkEscape) {
        if (oMyCurrentTimer.started) {
            var message = "Вы продолжаете работать над задачей. Все равно закрыть окно?";
            if (typeof evt == "undefined") {
                evt = window.event;
            }
            if (evt) {
                evt.returnValue = message;
            }
            return message;
        }
    }
};

$(document).on('click', '.js-send_feedback', function() {
    startLoader('small', '.js-send_feedback');
    $.post('/ajax/feedback/',
           $('.js-feedback_form').serialize(),
           function(html) {
               $('.js-modal_content').html(html);
               stopLoaders();
           }
    )
});

$(document).on('click', '.js-feedback', function () {
    $.get('/ajax/feedback/', function (data) {
        $('.js-modal_content').html(data);
        stopLoaders();
    });
});

$(document).on('shown.bs.modal', function () {
    startLoader('medium', '.js-feedback_loader');
});
$(document).on('click', '.toggle-password', function () {
    let input = $($(this).data("target"));
    if (input.attr("type") == "password") {
        input.attr("type", "text");
      } else {
        input.attr("type", "password");
      }
});
$(document).on('click', '.copy-password', function () {
    var copyText = $($(this).data("target")).val();
    console.log(copyText);
    var textarea = document.createElement('textarea');
    textarea.textContent = copyText;
    document.body.appendChild(textarea);
    var selection = document.getSelection();
    var range = document.createRange();
    range.selectNode(textarea);
    selection.removeAllRanges();
    selection.addRange(range);
    document.execCommand("copy");
    document.body.removeChild(textarea);
});
