/**
 * Created with PyCharm.
 * User: Gvammer
 * Date: 18.10.12
 * Time: 14:44
 */

var userOnline, usersOnline, userView;
var RANGE_BEFORE_END_OF_PAGE = 300;
var widget_chat_arLogMessages;
$(function () {
    userOnline = Backbone.Model.extend({
        avatar: '',
        username: '',
        full_name: '',
        userstatus: '',
        first: '',
        last: '',
        setFirst: function () {
            this.first = true;
        },
        setLast: function () {
            this.last = true;
        },
        setDefault: function () {
            this.first = false;
            this.last = false;
        }
    });

    usersOnline = Backbone.Collection.extend({
        model: userOnline,
        resetList: function () {
            var i = 0;
            for (var i_model in this.models) {
                i++;
                if (i == 1) {
                    this.models[i_model].setFirst()
                } else if (i == this.models.length) {
                    this.models[i_model].setLast()
                } else {
                    this.models[i_model].setDefault()
                }
            }
        }
    });

    userView = Backbone.View.extend({
        tagName: 'li',
        className: 'userRow',
        render: function () {
            $(this.el).html(this.template(this.model));
            if (this.model.first) {
                $(this.el).addClass('first');
            }
            if (this.model.last) {
                $(this.el).addClass('last');
            }
            if (!this.model.last && !this.model.first) {
                $(this.el).removeClass('last');
                $(this.el).removeClass('first');
            }
            return this;
        },
        template: function (userdata) {
            return '<img src="/static/images/primero_130.jpg" alt="' + userdata.get('username') + '">' +
                '<strong>' + userdata.get('username') + '</strong>' +
                '<p>"' + userdata.get('status') + '"</p>';
        }
    });

    widget_chat = new widgetObject({id: 'chat'});
    widget_chat.state = {
        taskCreate: false,
        hintOpened: {
            'Responsible': false,
            'Date': false,
            'Author': false
        }
    };

    widget_chat.onScrollRequest = false;
    widget_chat.$container = $('#chat');
    widget_chat.lastScrollTop = 0;
    widget_chat.ajaxUrl = '/messages_ajax/';
    widget_chat.input = widget_chat.$container.find('#wc_chat_message');
    widget_chat.$chatWindow = widget_chat.$container.find('#chatWindow');
    widget_chat.options = {
        'MESSAGE_TYPE': 'ALL',
        'OTHER_PROJECTS': true
    };
    widget_chat.optionsClasses = {
        'SYSTEM_MESSAGES': 'sm',
        'OTHER_PROJECTS': 'op',
        'USER_MESSAGES': 'um',
        'FILES': 'fs',
        'TODO': 'td',
        'BUGS': 'bg',
        'COMMITS': 'cm',
        'so': 'so',
        'ro': 'ro',
        'eo': 'eo'
    };
    widget_chat.$options = widget_chat.$container.find('.js-feed-options');

    widget_chat.messageListHelper = new messageListManager(widget_chat.$chatWindow, false, widget_chat_log_item_templates, true);

    $.extend(widget_chat, {
        'init': function () {
            widget_chat.arStartMessages = widget_chat_arLogMessages;
            widget_chat.messageListHelper.onAddMessage(function () {
                if (this.get('project')['id'] != window.currentProject) {
                    this.view.$el.addClass('js-' + widget_chat.optionsClasses['OTHER_PROJECTS']);
                }
                if (this.get('system')) {
                    this.view.$el.addClass('js-' + widget_chat.optionsClasses['SYSTEM_MESSAGES']);
                }
                else if (this.get('commit')) {
                    this.view.$el.addClass('js-' + widget_chat.optionsClasses['COMMITS']);
                }
                else if (this.get('files').length) {
                    this.view.$el.addClass('js-' + widget_chat.optionsClasses['FILES']);
                }
                else if (this.get('bug')) {
                    this.view.$el.addClass('js-' + widget_chat.optionsClasses['BUGS']);
                }
                else if (this.get('todo')) {
                    this.view.$el.addClass('js-' + widget_chat.optionsClasses['TODO']);
                }else if (this.get('type')) {
                    this.view.$el.addClass('js-' + widget_chat.optionsClasses[this.get('type')]);
                }
                else {
                    this.view.$el.addClass('js-' + widget_chat.optionsClasses['USER_MESSAGES']);
                }
            });

            var v = function () {
                widget_chat.options['MESSAGE_TYPE'] = $(this).val();
                $.cookie('FEED_OPTION_MESSAGE_TYPE', $(this).val());
            };
            var setGroupFlag = function () {
                widget_chat.messageListHelper.bNeedToGroup = widget_chat.options['MESSAGE_TYPE'] != 'COMMITS';
            };

            var resetTimeout = false;
            widget_chat.$options.find('.js-other-projects').click(function () {
                $.cookie('FEED_OPTION_OTHER_PROJECTS', $(this).is(':checked') ? 'Y' : 'N');
                widget_chat.reset();
                $('.toggle-messages.minimize').remove();
                setGroupFlag();
            });

            widget_chat.$options.find(':radio').click(v).click(function () {
                if (resetTimeout) clearTimeout(resetTimeout);
                resetTimeout = setTimeout(function () {
                    widget_chat.reset();
                    $('.toggle-messages.minimize').remove();
                    setGroupFlag();
                }, 200);
            });
            setGroupFlag();

//            widget_chat.messageListHelper.addMessages(widget_chat.arStartMessages);

            widget_chat.messageListHelper.reversed = true;
            widget_chat.bGettingFromServer = false;
            widget_chat.lastMessageId = -1;
            widget_chat.setLastId(widget_chat.arStartMessages);

            baseConnector.addListener('fs.comment.add', function (data) {
                if (!widget_chat.$container.is(':visible')) {
                    var $mContainer = $('.js-new-messages');
                    var newQty = parseInt($mContainer.text() || 0) + 1;
                    if (newQty > 99) newQty = 99;
                    $mContainer.text(newQty).show();
                }
                if (widget_chat.options['OTHER_PROJECTS']) {
                    if (data.project.id != window.currentProject) return;
                }
                switch (widget_chat.options['MESSAGE_TYPE']) {
                    case 'SYSTEM_MESSAGES':
                        if (!data.system) return;
                        break;
                    case 'USER_MESSAGES':
                        if (data.system || data.commit || data.files.length || data.todo || data.bug) return;
                        break;
                    case 'FILES':
                        if (!data.files.length) return;
                        break;
                    case 'COMMITS':
                        if (!data.commit) return;
                        break;
                    case 'TODO':
                        if (!data.todo) return;
                        break;
                    case 'BUGS':
                        if (!data.bug) return;
                        break;
                    case 'ro':
                        if (data.type !== 'ro') return;
                        break;
                    case 'so':
                        if (data.type !== 'so') return;
                        break;
                    case 'eo':
                        if (data.type !== 'eo') return;
                        break;
                    default:
                        break;
                }

                widget_chat.addMessageRow(data);
            });

//            baseConnector.addListener("userLogin", function(data){
//                widget_chat.userLogin(data);
//            });
//
//            baseConnector.addListener("userLogout", function(data){
//                widget_chat.userLogout(data);
//            });

            this.input.enterPressed(function (obj) {
                widget_chat.sendMessage($(obj).val());
                $(obj).val('');
            });

            function onScroll(type, data) {
                if (type == 'messages') {
                    if (!data.length) {
                        $('body').unbind('scroll.chat');
                        $(window).unbind('scroll.chat');
                        return;
                    }
                }
                var windowBottom = $(window).height() + $(window).scrollTop();
                if ($('.SUBCONTAINER:last').size() && windowBottom > $('.SUBCONTAINER:last').offset().top && $('.widget.chat').is(':visible')) {
                    if (!widget_chat.onScrollRequest) {
                        widget_chat.onScrollRequest = true;
                        widget_chat.getMessagesFromServer(onScroll);
                    }
                }
            }

            $(window).bind('scroll.chat', onScroll);
            $('body').bind('scroll.chat', onScroll);
        },
        'open': function() {
            if (!this.opened) {
                this.opened = true;
                widget_chat.getMessagesFromServer();
            }
        },
        'reset': function () {
            widget_chat.lastMessageId = -1;
            widget_chat.$chatWindow.css('height', widget_chat.$chatWindow.height());
            widget_chat.messageListHelper.clean();
//            this.$container.find('.task-message').remove();
            widget_chat.getMessagesFromServer(function () {
                widget_chat.$chatWindow.css('height', 'auto');
            });
        },
        'setLastId': function (aMessages) {
            for (var k in aMessages) {
                var mess = aMessages[k];
                if (widget_chat.lastMessageId == -1
                    || widget_chat.lastMessageId > parseInt(mess.id)) {
                    widget_chat.lastMessageId = parseInt(mess.id);
                }
            }
        },
        'userLogin': function (userdata) {
            if (!userList.get(userdata.id))
                userList.add(userdata);
        },
        'userLogout': function (userdata) {
            //TODO: доделать
            userList.remove(userOnline.get(userdata.id));
        },
        'getLastMessageId': function () {
            return this.lastMessageId;
        },
        'getMessagesFromServer': function (call) {
            if (this.bGettingFromServer) this.bGettingFromServer.abort();

            this.bGettingFromServer = PM_AjaxPost(
                this.ajaxUrl,
                {
                    'action': 'getMessages',
                    'last_id': this.getLastMessageId()
                },
                function (data) {
                    var message;
                    for (var k in data) {widget_chat.messageListHelper
                        message = data[k];
                        widget_chat.messageListHelper.reversed = false;
                        widget_chat.addMessageRow(message);
                        widget_chat.messageListHelper.reversed = true;
                    }
                    widget_chat.setLastId(data);
                    widget_chat.bGettingFromServer = false;
                    widget_chat.onScrollRequest = false;

                    if (call) {
                        call('messages', data);
                    }
                },
                'json'
            );
        },
        'sendMessage': function (message) {
            baseConnector.send("chat_message", {
                data: message
            });
        },
        'receiveMessage': function (message) {
//            console.log(message);
        },
        'addMessageRow': function (message) {
            this.lastScrollTop = $(window).scrollTop();
            widget_chat.messageListHelper.addMessages([message]);
            if (widget_chat.messageListHelper.reversed)
                this.scroll();
        },
        scroll: function () {
            if (widget_chat.$container.offset().top < $(window).scrollTop()) {
                if (this.lastScrollTop) {
                    var $lm = this.$container.find('.js-taskMessage').eq(0);
                    if (this.lastScrollTop)
                        $(window).scrollTop(this.lastScrollTop +
                            $lm.height() +
                            ($lm.css('margin-bottom').replace('px', '') * 1));
                }
            }
//            this.$chatWindow.parent().scrollTop(this.$chatWindow.scrollHeight || this.$chatWindow.get(0).scrollHeight);
        }
    });

    widget_chat.messageListHelper.playSound = true;
    widget_chat.init();

    var userList = new usersOnline;
    userList.$container = $('#chat .userList ul');
    userList.on('add', function (user) {
        userList.resetList();
        var view = new userView;
        view.model = user;

        this.$container.append(view.render().el);
    });


    document.mainController.widgetsData["chat"] = widget_chat;
});