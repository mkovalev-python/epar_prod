/**
 * Created with PyCharm.
 * User: Gvammer
 * Date: 24.02.13
 * Time: 21:57
 */
var messageListManager, taskMessageClass, taskMessageViewClass;
var SYSTEM_AVATAR_SRC = '/static/images/avatar_red_eye.png';
(function ($) {
    $(function () {
        taskMessageClass = Backbone.Model.extend({
            'url': function () {
                return '/message/' + this.id + '/';
            },
            'initialize': function () {

            },
            'saveToServer': function (callback) {
                var t = this;
                PM_AjaxPost(
                    '/messages_ajax/',
                    {
                        'action': 'update',
                        'id': t.get('id'),
                        'text': t.get('text'),
                        'checked': t.get('checked') ? 1 : 0,
                        'todo': t.get('todo') ? 1 : 0,
                        'bug': t.get('bug') ? 1 : 0
                    },
                    function (data) {
                        var i;
                        for (i in data) {
                            t.set(i, data[i]);
                        }
                        callback.call(t, data);
                    },
                    'json'
                );
//                this.save(null, {
//                    'success': function (model, data) {
//                        try {
//                            data = $.parseJSON(data);
//                            if (typeof(data) == typeof({}) && data.id) {
//                                for (var i in data) {
//                                    model.set(i, data[i]);
//                                }
//                            }
//
//                            callback.call(t, data);
//                        } catch (e) {
//                            console.log(e);
//                        }
//                    },
//                    'error': function (model, data) {
//                        console.log('Save error: ' + data);
//                    }
//                });
            }
        });

        taskMessageViewClass = Backbone.View.extend({
            editMode: false,
            tagName: 'div',
            tpl: '',
            editModeSaveButtonClass: 'js-saveMessageButton',
            editModeCancelButtonClass: 'js-cancelEditMessageButton',
            textareaClass: 'js-editMessageTextarea',
            messageTextBlockClass: 'js-messageDetailText',
            events: {
                "click .js-removeTaskMessage": 'removeMessage',
                "click .js-editTaskMessage": 'startEdit',
                "click .js-saveMessageButton": 'editConfirm',
                "click .js-cancelEditMessageButton": 'editCancel',
                "click .js-cancel-author-hide": 'cancelAuthorHidden',
                "click .js-cancel-resp-hide": 'cancelRespHidden',
                "click .js-show-commit-diff": 'showCommit',
                "click .js-show-file-diff": 'showFileDiff',
                "click .js-set-todo": 'setTodo',
                "click .js-set-bug": 'setBug',
                "click .js-check-bug": 'checkTodo',
                "click .js-check-todo": 'checkTodo'

            },
            'initialize': function (data) {
                this.tpl = data.templateHTML;
            },
            'setTodo': function (e) {
                if (e.currentTarget) {
                    this.setTaskOptions(e, 'todo')
                }
                return false;
            },
            'setBug': function (e) {
                if (e.currentTarget) {
                    this.setTaskOptions(e, 'bug')
                }
                return false;
            },
            'setTaskOptions': function (e, opt) {
                var $btn = $(e.currentTarget), setOpt;
                var view = this,
                    todo = this.model.get('todo'),
                    bug = this.model.get('bug'),
                    reverseOpt = {
                        bug: 'todo',
                        todo: 'bug'
                    };

                if ((todo != bug) && !($btn.is('.checked'))) {
                    $btn.siblings('.js-set-bug, .js-set-todo').toggleClass('checked');
                    this.model.set(reverseOpt[opt], false)
                }

                $btn.toggleClass('checked');
                setOpt = $btn.is('.checked');

                this.model.set(opt, setOpt);
                this.model.saveToServer(function (data) {
                    view.render();
                    $(window).triggerHandler('pmSetTodo', view.model);
                });
            },
            'checkTodo': function () {
                var check, view = this;
                check = !this.model.get('checked');
                this.model.set('checked', check);
                view.render();

                this.model.saveToServer(function (data) {
                    view.render();
                    $(window).triggerHandler('pmCheckTodo', view.model);
                });

                return false;
            },
            'showCommit': function (message) {
                if (message.currentTarget) {
                    var commit_body = $(message.currentTarget).parent().parent().find('.js-commit-body');
                    var url = $(message.currentTarget).attr('href');
                    $(message.currentTarget).prop('disabled', true);
                    $(commit_body).load(url, function (response, status) {
                        if (status == 'error') {
                            $(message.currentTarget).parent().remove();
                            alert('Не удалось загрузить коммит');
                        }
                        if (response) {
                            $(message.currentTarget).parent().remove();
                        }
                        else {
                            $(message.currentTarget).prop('disabled', false);
                        }
                    });
                }
                return false;
            },
            'showFileDiff': function (message) {
                if (message.currentTarget) {
                    $(message.currentTarget).parent().css('width', $(message.currentTarget).outerWidth() + 2);
                    if (message.currentTarget.nextElementSibling) {
                        $(message.currentTarget.nextElementSibling).slideToggle();
                    }
                }
            },
            'template': function (messageInfo) {
                var trimLinks = function (match) {
                    match = match.trim();
                    return "<a target='newtab' class='external-link' href='" + match + "'>" + match + "</a>";
                };
                var arKeys = {
                    'ID': messageInfo.id,
                    'TEXT': messageInfo.text.replace(new RegExp(/\[Q\]([^]+?)\[\/Q\]/mig), '<blockquote class="well">$1</blockquote>')
                        .replace(/(http|ftp|https):\/\/[\w-]+(\.[\w-]+)+([\w.,@?^=%&amp;:\/~+#-]*[\w@?^=%&amp;\/~+#-])?/mgi, trimLinks)
                        .replace(/(\r\n|\n)/mgi, "<br/>").replace(/(\t)/mgi, "&nbsp;&nbsp;&nbsp;&nbsp;"),
                    'DATE_CREATE': messageInfo.date,
                    'FILE_LIST': '',
                    'AVATAR_SRC': ''
                };
                arKeys['HIDDEN_LABEL'] = '';
                if (messageInfo.type) {
                    var a = {
                        'ro': 'Регулирующий орган',
                        'so': 'Сетевая организация',
                        'eo': 'Экспертная организация'
                    };
                    arKeys['HIDDEN_LABEL'] += a[messageInfo.type];
                }
                if (messageInfo.hidden_from_employee) {
                    arKeys['HIDDEN_LABEL'] += 'Скрыто от персонала <a href="#"><i class="fa fa-ban js-cancel-resp-hide"></i></a>';
                }
                arKeys['AVATAR'] = '';
                if (messageInfo.author.avatar) {
                    arKeys['AVATAR'] += '<img src="' + messageInfo.author.avatar + '" width="90px" class="media-object img-thumbnail"/>';
                } else if (messageInfo.author && messageInfo.author.last_name) {
                    var id = messageInfo.id;
                    var text = messageInfo.author.last_name[0] + messageInfo.author.name[0];
                    var color = messageInfo.author.avatar_color;
                    arKeys['AVATAR'] += $.createAvatar({'id': id, 'initials': text, 'color': color});
                }
                if (messageInfo.hidden) {
                    arKeys['HIDDEN_LABEL'] += 'Личное ';
                }
                if (messageInfo.hidden_from_clients) {
                    arKeys['HIDDEN_LABEL'] += 'Скрыто от клиентов <a href="#"><i class="fa fa-ban js-cancel-author-hide"></i></a>';
                }
                if (messageInfo.userTo.id) {
                    arKeys['USER_TO_NAME'] = ' для <b>' + messageInfo.userTo.name + '</b>';
                } else {
                    arKeys['USER_TO_NAME'] = '';
                }
                if (messageInfo.modifiedBy.last_name) {
                    arKeys['MODIFIED'] = '&nbsp;(изменил ' + messageInfo.modifiedBy.first_name + ' ' + messageInfo.modifiedBy.last_name + ' в ' + messageInfo.dateModify + ')';
                } else {
                    arKeys['MODIFIED'] = '';
                }
                if (messageInfo.author.id) {
                    arKeys['AUTHOR_NAME'] = messageInfo.author.name;
                    arKeys['AUTHOR_LAST_NAME'] = messageInfo.author.last_name;
                    arKeys['AUTHOR_USERNAME'] = messageInfo.author.username;
                    arKeys['AUTHOR_ID'] = messageInfo.author.id;
                    arKeys['AUTHOR_URL'] = '/user_detail/?id=' + messageInfo.author.id;
                } else {
                    arKeys['AUTHOR_NAME'] = 'сообщение';
                    arKeys['AUTHOR_LAST_NAME'] = 'Системное';
                    arKeys['AUTHOR_USERNAME'] = '';
                }

                arKeys['TASK_LINE'] = '';
                arKeys['PROJECT_LINE'] = '';
                arKeys['CONFIRMATION'] = '';
                arKeys['REPLY_BTN'] = '';
                arKeys['TODO_BTN'] = '<a class="to-do-button ' + (messageInfo.todo ? 'checked' : '') + ' js-set-todo" href="#">К обсуждению</a>';
                arKeys['BUG_BTN'] = '<a class="bug-button ' + (messageInfo.bug ? 'checked' : '') + ' js-set-bug" href="#">Ошибка</a>';
                //<label><input type="checkbox" '+(messageInfo.todo?'disabled':'')+' '+(messageInfo.checked?'checked':'')+' class=js-check-todo""/>
                if (messageInfo.confirmation) arKeys['CONFIRMATION'] = messageInfo.confirmation;

                if (messageInfo.task && messageInfo.task.name) {
                    if (messageInfo.project && messageInfo.project.name) {
                        arKeys['PROJECT_LINE'] = '<a href="' + messageInfo.project.url + '" class="message-info-title">' + messageInfo.project.name + '</a>';
                    }

                    if (messageInfo.task.parent && messageInfo.task.parent.id) {
                        var p = messageInfo.task.parent;
                        arKeys['TASK_LINE'] = arKeys['TASK_LINE'] + '<a href="' + p.url + '" class="message-desc-text">' + p.name + '</a> ';
                    }
                    arKeys['TASK_LINE'] = arKeys['TASK_LINE'] + '<a href="' + messageInfo.task.url + '" class="message-desc-text"><strong>' +
                        messageInfo.task.name + '</strong></a>';
                }
                if (messageInfo.author.id != document.mainController.userId)
                    arKeys['REPLY_BTN'] = '<a class="link js-reply" data-hidden="' + (messageInfo.hidden ? 1 : 0) + '" href="' + messageInfo.task.url + '" rel="' + messageInfo.author.id + '">Ответить</a>';


                if (messageInfo.system) {
                    arKeys.AVATAR_SRC = SYSTEM_AVATAR_SRC;
                } else if (messageInfo.avatar) {
                    arKeys.AVATAR_SRC = messageInfo.avatar;
                }

                if (messageInfo.files) {
                }

                if (!this.tpl) {
                    return '';
                }

                var t = this;
                var htmlTemplate = this.tpl;

                var k, strKey;
                for (k in arKeys) {
                    strKey = '#' + k + '#';
                    if (htmlTemplate.indexOf(strKey) > -1) {
                        htmlTemplate = htmlTemplate.replace(new RegExp(strKey, 'mig'), arKeys[k]);
                    }
                }
                return htmlTemplate;
            },
            'render': function (params) {
                if (!params)
                    params = {};

                if (this.model.get('invisible')) {
                    this.$el.hide();
                } else {
                    this.$el.show();
                }
                var qa = this.template(this.model.toJSON());
                this.$el.html(qa).addClass('task-message');
//                var $messageTextBlock = this.$el.find('.js-taskMessageText');

                if (!this.model.get('text') && !this.model.get('files')) {
                    return false;
                }

                if (!this.model.get('author').id) {
                    this.$('.js-author-block').hide();
                }

//                if (!this.model.get('avatar') && this.model.get('author').id){
//                    this.$('.js-avatarBlock').hide();
//                    $messageTextBlock.removeClass('Img');
//                }
                var aFiles = this.model.get('files');

                if (aFiles) {

                    var aFilesHtml = this.getFilesHtml();
                    var aPictures = aFilesHtml['pictures'];
                    var aOtherFiles = aFilesHtml['other'];
                    var $pictures = $('<div class="message-pictures clearfix"></div>'),
                        $otherFiles = $('<div class="message-other-files clearfix"></div>');

                    var exist;
                    var $filesListblock = this.$('.js-filesList').eq(0);
                    if (aPictures) {
                        exist = false;
                        for (i in aPictures) {
                            exist = true;
                            if (aPictures.hasOwnProperty(i))
                                $pictures.append(aPictures[i]);
                        }
                        if (exist)
                            $filesListblock.append($pictures);
                    }

                    if (aOtherFiles) {
                        exist = false;
                        for (i in aOtherFiles) {
                            exist = true;
                            if (aOtherFiles.hasOwnProperty(i))
                                $otherFiles.append(aOtherFiles[i]);
                        }
                        if (exist)
                            $filesListblock.append($otherFiles);
                    }
                }

                this.$el.addClass('row-fluid show-grid js-taskMessage').data('id', this.model.id);
                var actTodo = 'removeClass', actBug = actTodo;
                if (this.model.get('todo') || this.model.get('bug')) {
                    var $todoCheckBox = $('<i class="fa js-check-todo"></i>').attr('rel', this.model.id);

                    if (this.model.get('checked')) {
                        $todoCheckBox.addClass('fa-check-square-o');
                    } else {
                        $todoCheckBox.addClass('fa-square-o');
                    }
                    $todoCheckBox.appendTo(this.$('.js-taskMessageText'));

                    if (this.model.get('todo')) actTodo = 'addClass';
                    if (this.model.get('bug')) actBug = 'addClass';
                } else {
                    this.$('.js-check-todo').remove();
                }
                this.$('.message')[actTodo]('todo-message');
                this.$('.message')[actBug]('bug-message');

                if (this.model.get('canEdit')) {
                    this.$('.js-editTaskMessage').show();
                }
                if (this.model.get('canDelete')) {
                    this.$('.js-removeTaskMessage').show();
                }
                if (this.model.get('noveltyMark')) {
                    this.$el.addClass('new-message js-new');
                }
//                this.$('.fnc').fancybox();

                this.delegateEvents();

                return this;
            },
            'getFilesHtml': function () {
                var aPictures = [], aOtherFiles = [], aFiles = this.model.get('files');
                for (var i in aFiles) {
                    var file = aFiles[i];
                    var rowTemplate;

                    if (file.is_picture) {
                        rowTemplate = '<a class="fnc" href="#URL#"><img src="#URL_SMALL#" /></a>';
                    } else {
                        rowTemplate = '<a #ADD# href="#VIEW_URL#">#NAME#</a>&nbsp;<a href="#URL#" class="icon-download-alt icon-#EXTENSION#"></a>';
                    }
                    if (file.viewUrl) {
                        rowTemplate = rowTemplate.replace(/\#VIEW_URL\#/mgi, file.viewUrl);
                        rowTemplate = rowTemplate.replace(/\#ADD\#/mgi, 'class="fnc_ajax"');
                    } else {
                        rowTemplate = rowTemplate.replace(/\#VIEW_URL\#/mgi, file.url);
                        rowTemplate = rowTemplate.replace(/\#ADD\#/mgi, '');
                    }
                    rowTemplate = rowTemplate.replace(/\#URL\#/mgi, file.url);
                    rowTemplate = rowTemplate.replace(/\#NAME\#/mgi, file.name);
                    rowTemplate = rowTemplate.replace(/\#EXTENSION\#/mgi, file.type);
                    rowTemplate = rowTemplate.replace(/\#URL_SMALL\#/mgi, file.thumb100pxUrl);

                    if (file.is_picture) {
                        aPictures.push($(rowTemplate));
                    } else {
                        aOtherFiles.push($(rowTemplate))
                    }
                }

                return {
                    'pictures': aPictures,
                    'other': aOtherFiles
                }
            },
            'removeMessage': function () {
                var t = this,
                    model = this.model;
                if (confirm("Вы действительно хотите удалить сообщение?")) {
                    model.destroy({
                        'success': function (model, response) {
                            if (response == 'Message has been deleted')
                                t.remove();
                        }
                    });
                }

                return false;
            },
            'startEdit': function () {
                var t = this;
                if (!t.editMode) {
                    t.editMode = true;

                    var $textarea = $('<textarea></textarea>').addClass('form-control ' + this.textareaClass);
                    var $messageTextBlock = this.$('.js-messageDetailText');
                    var $saveButton = $('<button></button>').text('Сохранить').addClass('btn btn-success')
                        .addClass(this.editModeSaveButtonClass);
                    var $cancelButton = $('<button></button>').text('Отмена').addClass('btn btn-danger')
                        .addClass(this.editModeCancelButtonClass);
                    var tags = new RegExp('\<[^>]+\>', 'mig');
                    $messageTextBlock.replaceWith(
                        $textarea.val(
                            htmlspecialchars_decode(t.model.get('text'))
                        )
                    );
                    this.$('.js-quote').hide();
                    this.$('.js-reply').hide();
                    this.$('.js-taskMessageText').append($saveButton, $cancelButton)
                }

                return false;
            },
            'editCancel': function () {
                this.editMode = false;
                this.$('.js-quote').show();
                this.$('.js-reply').show();
                this.render();
            },
            'editConfirm': function () {
                this.editMode = false;
                var $textarea = this.$('.' + this.textareaClass);
                this.$('.js-quote').show();
                this.$('.js-reply').show();
                var newText = $('<div />').text($textarea.val()).html();
                var view = this;
                this.model.set('text', newText);
                this.model.saveToServer(function (data) {
                    view.render();
                });
            },
            'cancelAuthorHidden': function () {
                var view = this;
                this.model.set('hidden_from_clients', false);
                this.model.saveToServer(function (data) {
                    view.render();
                });
                return false;
            },
            'cancelRespHidden': function () {
                var view = this;
                this.model.set('hidden_from_employee', false);
                this.model.saveToServer(function (data) {
                    view.render();
                });
                return false;
            }
        });

        messageListManager = function ($element, taskId, arMessageTpl, needToGroup) {
            this.taskId = taskId;
            this.$commentsContainer = $element;
            if (arMessageTpl)
                this.messageTemplates = arMessageTpl;
            else
                this.messageTemplates = {'template': ''};
            this.showLast = 7;
            this.callbacks = [];
            this.addCallbacks = [];
            this.bNeedToGroup = !!needToGroup;
            this.init();
        };

        messageListManager.prototype = {
            init: function () {
                var t = this;

                var collectionClass = Backbone.Collection.extend({
                    model: taskMessageClass
                });
                this.messageList = new collectionClass();
                this.messageList.url = function () {
                    return '/message';
                };

                this.messageList.on("add", function (message) {
                    if (t.taskId)
                        message.set('task', t.taskId);

                    var code = (message.get('code') + '').toLowerCase();
                    var codeTpl = t.messageTemplates[code];
                    if (!message.view) {
                        message.view = new taskMessageViewClass({
                            'model': message,
                            'templateHTML': codeTpl ?
                                codeTpl : t.messageTemplates['template']
                        });
                    }
                    message.view.render();

                    for (var i in t.addCallbacks) {
                        t.addCallbacks[i].call(message);
                    }

                    var func;
                    if (t.reversed) {
                        func = 'prepend';
                        if (message.get('userTo') && message.get('userTo')['id'] == document.mainController.userId) {
                            var mes = message.view.$el.children().find('img, .js-quote, .js-answer').remove().end().html(),
                                mesType;
                            if (code == 'warning') {
                                mesType = "warning"
                            }
                            else {
                                mesType = "info"
                            }
                            if (!message.get('init'))
                                toastr[mesType](mes);
                        }

                        if (!message.get('init'))
                            knock();
                    } else {
                        func = 'append';
                    }
                    if (message.get('userTo') && message.get('userTo')['id'] == document.mainController.userId) {
                        message.view.$el.addClass('for_current_user');
                    }

                    /* Mininimize system messages */
                    var subCode = message.get('code');
                    if (subCode == null) {
                        subCode = 'MESSAGES';
                    }

                    var $lastContainer = t.$commentsContainer.find('.SUBCONTAINER:last'),
                        isNewMessage = message.get('noveltyMark'),
                        isNewSubContainerCreated = false;

                    if (
                        !t.bNeedToGroup || !$lastContainer.hasClass(subCode) ||
                        isNewMessage ||
                        subCode === 'MESSAGES'
                    ) { //create new subcontainer

                        var $newSubContainer = $('<div class="' + subCode + ' SUBCONTAINER"></div>');
                        if (isNewMessage && t.$commentsContainer.length > 0 && t.reversed) {
                            t.$commentsContainer.prepend($newSubContainer);
                        } else {
                            t.$commentsContainer.append($newSubContainer);
                        }
                        isNewSubContainerCreated = true;
                    }

                    var $firstSubContainer = t.$commentsContainer.find('.SUBCONTAINER:first'),
                        $lastSubContainer = t.$commentsContainer.find('.SUBCONTAINER:last');


                    if (isNewMessage && t.$commentsContainer.length > 0 && t.reversed) {
                        $firstSubContainer[func](message.view.$el);
                    } else {
                        $lastSubContainer[func](message.view.$el);
                    }

                    if (!isNewSubContainerCreated) message.view.$el.hide();
                    /* /Mininimize system messages */

                });

                this.messageList.on("remove", function (message) {
                    message.view.$el.remove();
                });

                setTimeout(function () {
                    for (var i in t.callbacks) {
                        t.callbacks[i].call(t);
                    }
                }, 0);
            },
            addMessages: function (aMessagesData) {
                var i, l = aMessagesData.length, t = this, $showAllBtn = $('.js-show-all');
                if (!aMessagesData) return;

                if (this.showLast > 0) { //TODO: все, что в этом услови, должно быть во вьюхах
                    for (var k in aMessagesData) {
                        i++;
                        var mes = aMessagesData[k];

                        if (i < l - this.showLast) {
                            mes['invisible'] = true;
                        }

                        if (i == l - this.showLast && l > this.showLast) {
                            $showAllBtn.show();
                        }

                        this.messageList.add([mes]);
                    }
                    $showAllBtn.click(function () {
                        $('.js-taskMessage').show();
                        $(this).remove();
                    });
                } else {
                    this.messageList.add(aMessagesData);
                }

                /* Minimize messages */

                var $subContainer = $('.SUBCONTAINER'),
                    firstItems,
                    lastItems = 6;

                if ($('.SUBCONTAINER:lt(2)').hasClass('MESSAGES') || !$subContainer.hasClass('MESSAGES')) {
                    firstItems = 2
                } else {
                    firstItems = $('.MESSAGES').index('.SUBCONTAINER') + 1
                }


                //first user message + messages before; last 6 messages stay visible
                if (t.taskId) {
                    $('.SUBCONTAINER:lt(' + firstItems + '), .SUBCONTAINER:gt(-' + lastItems + ')').addClass('show-msg');
                }

                $('.js-taskMessage:hidden').closest('.SUBCONTAINER').each(function () {
                    if ($(this).find('.js-taskMessage').size() <= 1) return;
                    $(this).find('.js-btn-minimize').remove();

                    var hiddenMsgsQty = $(this).find('.js-taskMessage:hidden').size();
                    var $btnMinimize = $(
                        '<div class="toggle-messages minimize js-btn-minimize">' +
                        '<span class="btn btn-xs"><span class="fa fa-caret-down">' +
                        '</span>&nbsp;&nbsp;Еще ' + hiddenMsgsQty + '...</span></div>'
                    );

                    $btnMinimize.click(function () {
                        $(this).siblings().show();
                        $(this).remove();
                    });
                    $(this).append($btnMinimize);
                });

                /* /Minimize messages */
            },

            ready: function (callback) {
                this.callbacks.push(callback);
            },

            onAddMessage: function (callback) {
                this.addCallbacks.push(callback);
            },

            clean: function () {
                this.messageList.remove(this.messageList.models);
                $('.SUBCONTAINER').remove();
            },

            getById: function (id) {
                return this.messageList.get(parseInt(id));
            },

            forEach: function (callback) {
                return this.messageList.each(callback);
            },

            forEachBack: function (callback) {
                for (var i = this.messageList.length - 1; i >= 0; i--) {
                    var myModel = this.messageList.models[i];
                    callback(myModel, i);
                }
            }
        }
    });
})(jQuery);