/**
 * Created with PyCharm.
 * User: Gvammer
 * Date: 24.02.13
 * Time: 21:57
 */
var CRITICALLY_THRESHOLD = 0.7;
(function ($) {
    var showError = function (text) {
        $('<div></div>').addClass('popup system').append('<a href="#" class="popup-close" onclick="$(this).closest(\'.popup\').remove();return false;"><i class="fa fa-times"></i></a>').append(text).appendTo('body').show();
    };

    window.taskClass = Backbone.Model.extend({
        'url': function () {
            return '/task/' + this.id + '/';
        },
        'initialize': function () {
            if (arTimers && arTimers[this.id]) {
                this.set('timer', arTimers[this.id]);
            }
        },
        'getFromServer': function (callback) {
            var t = this;
            console.log('fetching task');
            this.fetch({
                'success': function (model, data) {
                    console.log(data);
                    try {
                        data = $.parseJSON(data);
                        if (typeof (data) == typeof ({}) && data.id) {
                            for (var i in data) {
                                model.set(i, data[i]);
                            }
                        }
                    } catch (e) {
                        console.log('Parse error');
                    }
                    try {
                        if (callback)
                            callback.call(t);
                    } catch (e) {
                        console.log('Callback error');
                    }
                },
                'error': function (model, data) {
                    console.log('Read task error');
                }
            });
        },
        'getMenuItems': function () {
            var arItems = [];
            if (this.get('canEdit')) {
                arItems.push({
                    'itemClass': 'Edit',
                    'itemText': 'Изменить',
                    'itemMethod': 'editTask',
                    'icon': 'edit'
                });
                arItems.push({
                    'itemClass': 'Deadline',
                    'itemText': 'Сроки',
                    'itemMethod': 'setDeadline',
                    'icon': 'calendar'
                });
            }

            if (this.get('observer')) {
                arItems.push({
                    'itemClass': 'ResetPlanning',
                    'itemText': 'Не наблюдаю',
                    'itemMethod': 'stopObserve',
                    'icon': 'eye-slash'
                });
            } else {
                arItems.push({
                    'itemClass': 'BringPlanning',
                    'itemText': 'Наблюдаю',
                    'itemMethod': 'startObserve',
                    'icon': 'eye'
                });
            }
            if (this.get('canSetOnPlanning')) {
                if (this.get('onPlanning')) {
                    arItems.push({
                        'itemClass': 'ResetPlanning',
                        'itemText': 'Выбрать наименьшую оценку',
                        'itemMethod': 'closePlanning',
                        'icon': 'list-alt'
                    });
                } else {
                    arItems.push({
                        'itemClass': 'BringPlanning',
                        'itemText': 'На согласование',
                        'itemMethod': 'addToPlaning',
                        'icon': 'users'
                    });
                }
            }

            if (!this.get('closed') && !this.get('subtasksQty')) {
                var status = this.get('status');

                if (status == 'ready') {
                    arItems.push({
                        'itemClass': 'SetRevision',
                        'itemText': 'На доработку',
                        'itemMethod': 'setRevision',
                        'icon': 'thumbs-down'
                    });
                } else if (status == 'not_approved') {
                    if (this.get('canApprove')) {
                        arItems.push({
                            'itemClass': 'SetRevision',
                            'itemText': 'Подтвердить выполнение',
                            'itemMethod': 'approveTask',
                            'icon': 'check-square-o'
                        });
                    }
                } else {
                    arItems.push({
                        'itemClass': 'SetReady',
                        'itemText': 'На проверку',
                        'itemMethod': 'setReady',
                        'icon': 'check-square-o'
                    });
                }
            }

            //if (this.get('canBaneUser')) {
            //	arItems.push({
            //		'itemClass': 'baneUser',
            //		'itemText': 'Исполнитель не справился',
            //		'itemMethod': 'baneUser',
            //		'icon': 'thumbs-down'
            //	});
            //}

            if (this.get('canSetCritically')) {
                var criticallyObj = {
                    'itemClass': 'Critically',
                    'itemMethod': 'toggleCritically'
                };
                if (this.get('critically') > CRITICALLY_THRESHOLD) {
                    criticallyObj['icon'] = 'ban';
                    criticallyObj['itemText'] = 'Не важно';
                } else {
                    criticallyObj['icon'] = 'exclamation-circle';
                    criticallyObj['itemText'] = 'Важно';
                }
                arItems.push(criticallyObj);
            }

            arItems.push({
                'itemClass': 'Color',
                'itemText': 'Тип затрат',
                'itemMethod': 'setColor',
                'icon': 'th-large'
            });

            if (this.get('canRemove')) {
                arItems.push({
                    'itemClass': 'Remove',
                    'itemText': 'Удалить',
                    'itemMethod': 'removeTask',
                    'icon': 'times-circle'
                });
            }

            return arItems;
        }
    });

    window.taskList = Backbone.Collection.extend({'model': window.taskClass});

    window.taskViewClass = Backbone.View.extend({
        events: function () {
            if (this.options.events) {
                return this.options.events
            } else
                return {
                    "click a.js-task_play:not('.started'):not('.disabled')": "taskStart",
                    "click a.js-task_play.started": "showPauseDialog",
                    "click a.pause_comment_success": "taskStop",
                    "click a.pause_comment_cancel": "taskStop",
                    "click a.add-subtask": "addSubTask",
                    "click a.js-task_menu": "showMenu",
                    "click a.js-task_done:not('.closed')": "closeTask",
                    "click a.js-task_done.closed": "openTask",
                    "click a.js-select_resp": "showResponsibleMenu",
                    "click a.js-resp-approve": "responsibleApprove",
                    "click .jsPlanTimeList a": "changePlanTime",
                    "click a.js-task_approve": "approveTask",
                    "click a.jsPlanTimeHolder": "focus",
                    "keyup .js-input-plan": "changePlanTime",
                }
        },
        'initialize': function () {
            if (!this.options.responsibleMenuUrl) {
                this.options.responsibleMenuUrl = '/ajax/responsible_menu/';
            }
            if (!this.el) {
                this.$el = $('.taskLine_' + this.model.id);
                this.el = this.$el.get(0);
            }
            this.arPlanTimes = [
                // [10000, '~ 10 тыс. р.'],
                // [100000, '~ 100 тыс. р.'],
                // [1000000, '~ 1 млн. р'],
                // [10000000, '~ 10 млн. р'],
                // [100000000, '~ 100 млн. р'],
                // [100000000, '~ 1 млрд. р'],
            ];
        },
        'focus': function (e) {
            var $target = $(e.currentTarget);
            setTimeout(function () { $target.parent().find('.js-input-plan:visible').focus(); }, 200);
        },
        'createEl': function () {
            this.$el = $('<div></div>')
                .attr('id', 'taskLine_' + this.model.id + '')
                .addClass('task clearfix')
                .attr('data-taskid', this.model.id);
            this.el = this.$el.get(0);

            return this;
        },
        'getUrl': function () {
            return '/task_detail/?id=' + this.model.id;
        },
        'showModalStart': function () {
            //todo: разработчик нажимает раньше, чем узнает
            $('<div class="modal fade"><div id="previewModal" class="modal fade wiki-modal in" style="display: block;" aria-hidden="false"><div class="modal-dialog"><div class="modal-content ui-resizable"></div></div></div>')
                .find('modal-content').append('<h3>Сколько примерно времени у вас займет данный расчет?</h3>')
                .append('<select></select>').end().modal('show');
        },
        'template': function (taskInfo, params) {
            if (!params) params = {};
            var linkSpanReplace = function ($link) {
                var $span = $('<span></span>').addClass($link.get(0).className).text($link.text());
                $link.replaceWith($span);
                return $span;
            };
            if (!window.taskHtml) return false;
            var html = window.taskHtml;
            html = html.replace(/\#TASK\_ID\#/ig, taskInfo.id);
            html = html.replace(/\#TASK\_NUMBER\#/ig, taskInfo.number);
            html = html.replace(/\#TASK\_URL\#/ig, taskInfo.url);
            html = html.replace(/\#TASK\_NAME\#/ig, taskInfo.name);
            html = html.replace(/\#PARENT\_NAME\#/ig, taskInfo.parentName);
            if (taskInfo.hasOwnProperty('messages')) {
                html = html.replace(/\#MESSAGES\#/ig, taskInfo.messages);
            }

            var sLastMessage;
            if (taskInfo.last_message && taskInfo.last_message.author)
                sLastMessage = taskInfo.last_message.author + ': ' + taskInfo.last_message.text;
            else if (taskInfo.last_message)
                sLastMessage = taskInfo.last_message.text;
            else
                sLastMessage = '';

            html = html.replace(/\#LAST\_MESSAGE\#/ig, sLastMessage);

            if (!taskInfo.subtasksQty) taskInfo.subtasksQty = '';
            html = html.replace(/\#ACTIVE\_SUBTASK\_QTY\#/ig, taskInfo.subtasksQty);

            if (!taskInfo.deadline) taskInfo.deadline = '';
            if (taskInfo.deadline) taskInfo.deadline = 'до&nbsp;' + taskInfo.deadline;
            html = html.replace(/\#DEADLINE#/ig, taskInfo.deadline);

            var sFileList = '';
            var url;
            for (var file_path in taskInfo.files) {
                var file = taskInfo.files[file_path];
                console.log(taskInfo)
                    if (file.category!==null)
                     url = '/files/#'+ taskInfo.category;
                else
                     url = '/files/';

                sFileList = '<span>&nbsp;</span><a class="js_task_responsibles" href="' + url + '">Папка с файлами</a>';

            }
            html = html.replace(/\#FILE\_LIST#/ig, sFileList);


            var $row = $(html),
                parent = taskInfo.parent;

            var oTaskContainers = {
                '$taskNameCont': $row.find('.task-line_name'),
                '$statusContainer': $row.find('.task-name_status'),
                '$addSubtaskColumn': $row.find('.add-subtask'),
                '$timer': $row.find('.js-time'),
                '$responsibleLink': $row.find('.js_task_responsibles .dropdown'),
                '$planTime': $row.find('.task-plantime'),
                '$planTimeReg': $row.find('.task-plantime-reg'),
                '$planTimeMain': $row.find('.task-plantime-main')
            };

            if (params.timerTag) {
                var $newTimerTag = $('<' + params.timerTag + ' data-toggle="dropdown" class="js-time"></' + params.timerTag + '>');
                oTaskContainers.$timer
                    .replaceWith($newTimerTag);
                oTaskContainers.$timer = $newTimerTag;
            }

            this.$el.removeClass('ready');

            if (taskInfo.status === 'ready') {
                this.$el.addClass('ready');
            }

            oTaskContainers.$statusContainer.addClass(taskInfo.color);

            if (parent) {
                // oTaskContainers.$addSubtaskColumn.hide();
            }

            var a = [
                oTaskContainers.$planTime,
                oTaskContainers.$planTimeReg,
                oTaskContainers.$planTimeMain,
            ];

            var t = this;


            a.forEach(function ($cont) {
                var prop = $cont.data('prop');
                var title = $cont.data('title');
                if (taskInfo[prop])
                    taskInfo[prop] = '' + ( taskInfo[prop]  ) + ' руб.';
                else
                    taskInfo[prop] = '';

                var sPlanTime = '';
                if (taskInfo.planTime || taskInfo.onPlanning || taskInfo.canSetPlanTime) {
                    sPlanTime += '<span class="dropdown" style="opacity: .5">' + title + ' </span>' +
                        '<span class="dropdown">' +
                        (taskInfo.subtasksQty || !taskInfo.canSetPlanTime ? '' : '<a data-toggle="dropdown" class="tasklist-plan-time jsPlanTimeHolder">')
                        + ((taskInfo[prop] ? parseFloat(taskInfo[prop]).toLocaleString('ru') : 0)  || (taskInfo.subtasksQty ? '0' : 'План'))
                        + (taskInfo.subtasksQty || !taskInfo.canSetPlanTime ? '' : '</a> ');

                    sPlanTime += '<ul class="dropdown-menu jsPlanTimeList" >';

                    for (var i in t.arPlanTimes) {
                        var planTime = t.arPlanTimes[i];
                        sPlanTime += '<li><a rel="' + planTime[0] + '">' + planTime[1] + '</a></li>';
                    }
                    sPlanTime += '<li><input type="text" style="border: 0;padding: 5px 15px;" class="js-input-plan"></li>';
                    sPlanTime += '</ul>';
                    sPlanTime += '</span>';
                    sPlanTime += '<span class="dropdown"></span>';
                    if (taskInfo.planTimes && taskInfo.planTimes.length > 0) {
                        sPlanTime += '<span class="dropdown arrow">';
                        // sPlanTime += '<a data-toggle="dropdown" ><b class="caret"></b></a>';
                        sPlanTime += '<div class="dropdown-menu pull-right">';
                        for (i in taskInfo.planTimes) {
                            var oPlanTime = taskInfo.planTimes[i];

                            sPlanTime += '<a href="' + oPlanTime.user_url + '" rel="' + oPlanTime.user_id + '">' + oPlanTime.user_name + '</a>&nbsp;-&nbsp;' + oPlanTime.time + '&nbsp; руб<br />';
                        }
                        sPlanTime += '</div>';
                        sPlanTime += '</span>';
                    }
                } else {
                    sPlanTime += '&nbsp;';
                }
                $cont.append(sPlanTime);

            });


            var sTimerListTpl = '<a href="#URL#" rel="#">#USER#</a> - <span>#HOURS#:#MINUTES#:#SECONDS#</span><br />';
            if (taskInfo.timers && taskInfo.timers.length > 0) {
                var $realTimeListHolder = $('<div class="dropdown-menu pull-right"></div>').insertAfter(oTaskContainers.$timer);
                for (var i in taskInfo.timers) {
                    var realTime = taskInfo.timers[i];
                    var sCTHTML = sTimerListTpl.replace('#URL#', realTime.user_url);
                    sCTHTML = sCTHTML.replace('#USER#', realTime.user);
                    sCTHTML = sCTHTML.replace('#HOURS#', ((realTime.time.hours < 10 ? '0' : '') + realTime.time.hours));
                    sCTHTML = sCTHTML.replace('#MINUTES#', ((realTime.time.minutes < 10 ? '0' : '') + realTime.time.minutes));
                    sCTHTML = sCTHTML.replace('#SECONDS#', ((realTime.time.seconds < 10 ? '0' : '') + realTime.time.seconds));

                    $realTimeListHolder.append(sCTHTML);
                }
            }

            var $buttonClose = $row.find('.js-task_done');
            var $approveBtn = $row.find('.js-task_approve');
            if (taskInfo.subtasksQty) {
                $buttonClose.hide();
                $approveBtn.hide();
            } else {
                if (taskInfo.closed) {
                    $buttonClose.hide();
                    $approveBtn.hide();
                } else {
                    if (taskInfo.status == 'not_approved') {
                        if (taskInfo.canApprove)
                            $approveBtn.show();

                        $buttonClose.hide();
                    } else {
                        $approveBtn.hide();
                        $buttonClose.show();
                        var $closeIcon = $buttonClose.find('.fa');
                        if (taskInfo.canClose) {
                            $closeIcon.removeClass('fa-check').addClass('fa-check').attr('title', 'Закрыть расчет');
                        } else {
                            $closeIcon.removeClass('fa-check').addClass('fa-check').attr('title', 'На проверку');
                            if (taskInfo.status == 'ready') {
                                $closeIcon.hide();
                            }
                        }
                    }
                }
            }


            var $buttonStart = $row.find('.js-task_play');
            if (!taskInfo.closed) {
                if (taskInfo.startedTimerExist)
                    $buttonStart.addClass('started').find('.fa').removeClass('fa-play-circle').addClass('fa-pause');
                else
                    $buttonStart.removeClass('started').find('.fa').removeClass('fa-pause').addClass('fa-play-circle');
            }
            if (!params.responsibleTag) params.responsibleTag = 'a';
            var $respLink = $('<' + params.responsibleTag + '></' + params.responsibleTag + '>').attr({
                'data-toggle': 'dropdown'
            }).addClass('js-select_resp').appendTo(oTaskContainers.$responsibleLink);

            var rName = [];
            if (taskInfo.resp && taskInfo.resp[0] && taskInfo.resp[0]['name']) {
                for (var i in taskInfo.resp) {
                    var respName = taskInfo.resp[i];
                    rName.push(respName['name']);
                }
                $respLink.text(rName.join(', '));
            } else if (taskInfo.recommendedUser && taskInfo.needRespRecommendation && !taskInfo.subtasksQty) {
                var restRec = $respLink.text(taskInfo.recommendedUser.name + '?').addClass('recommended');
                $('<a href=""></a>').addClass('fa fa-thumbs-o-up fa-lg fa-border js-resp-approve')
                    .attr('rel', taskInfo.recommendedUser.id).insertAfter(restRec);
            } else {
                $respLink.text('Нет');
            }
            var v, todo;
            for (v in taskInfo.todo) {
                todo = taskInfo.todo[v];
                $row.find('.js-todo').append(
                    '<i class="fa fa' + (todo.checked ? '-check' : '') + '-square-o ' + (todo.bug ? 'bug' : '') + '"></i>'
                )
            }

            return $row.html();
        },
        'disableTimerButton': function () {
            this.$('.js-task_play').addClass('disabled');
        },
        'enableTimerButton': function () {
            this.$('.js-task_play').removeClass('disabled').removeClass('transparent');
        },
        'hideTimerButton': function () {
            this.$('.js-task_play').addClass('disabled transparent');

        },
        'render': function () {
            var templateParams = {};

            var playBtnStatus = 'enabled';
            if (this.model.get('subtasksQty') > 0) {
                templateParams.responsibleTag = 'span';
                templateParams.timerTag = 'span';
                playBtnStatus = 'transparent';
            }
            var oTime = this.model.get('time');
            var allTime = oTime.seconds + oTime.hours + oTime.minutes;
            if (!allTime) {
                templateParams.timerTag = 'span';
            }

            this.$el.html(this.template(this.model.toJSON(), templateParams));

            if (this.model.get('loader')) {
                var $closeBtn = this.$el.find('.js-task_done');
                startLoader('tiny', $closeBtn);
                $closeBtn.hide();
            } else {
                stopLoader($('.loader.tiny'));
            }

            if (this.model.get('closed')) {
                this.$el.addClass('closed');
                playBtnStatus = 'disabled';
            } else {
                this.$el.removeClass('closed');
            }

            if (this.model.get('onPlanning'))
                this.$el.addClass('onplan').attr('data-onplan', 'Y');
            else this.$el.removeClass('onplan').attr('data-onplan', 'N');

            var iSTUID = this.model.get('startedTimerUserId');
            if (iSTUID) {
                this.$el.attr('data-started_timer_user_id', iSTUID);
                if (window.baseUserParams.userId != iSTUID) playBtnStatus = 'disabled';
            }

            if (this.model.get('critically') > CRITICALLY_THRESHOLD) this.$el.addClass('critically').parent('.task-wrapper').addClass('critically');
            else this.$el.removeClass('critically').parent('.task-wrapper').removeClass('critically');

            if (this.model.get('startedTimerExist')) this.$el.addClass('started');
            else this.$el.removeClass('started');

            if (!this.model.get('viewed')) this.$el.addClass('newEvent');
            else this.$el.removeClass('newEvent');

            //создание таймера и добавление его модельке
            var timer = this.model.get('timer');
            if (this.model.get('time') && !this.model.get('timer')) {
                timer = this.createTimer(this.model.get('time'));

                this.model.set('timer', timer);
            }

            if (timer) {
                timer.container = this.$el.find('.js-time').get(0);

                $(timer.container).html(timer.toString());

                if (this.model.get('startedTimerExist')) {
                    timer.start();
                } else {
                    timer.stop();
                }
            } else {
                this.$el.find('.js-time').html('00:00:00')
            }

            if (playBtnStatus == 'disabled') {
                this.disableTimerButton();
            } else if (playBtnStatus == 'enabled') {
                this.enableTimerButton();
            } else {
                this.hideTimerButton();
            }

            var avatar = this.$el.find('.js-avatar-container');
            if (avatar.get(0) && this.model.get('avatar')) {
                avatar.empty().attr('rel', JSON.stringify(this.model.get('avatar')));
                $.updateAvatar(
                    avatar,
                    {size: avatar.data('size') || 30}
                );
            }

            this.delegateEvents();

            if (this.$el.parent().get(0))
                setTaskCellsHeight(this.$el);

            this.$('.js-name-link').click(function () {
                if (false) { //$(window).width() > 420
                    $('.js-frame-mode').find('iframe')
                        .each(function () {
                            $(this.contentDocument).empty()
                        })
                        .attr('src', $(this).attr('href') + '&frame_mode=Y').css('height', $(window).height())
                        .css('background-color', 'white')
                        .load(function () {
                            $(this.contentDocument).on('click', 'a', function () {
                                var href = $(this).attr('href');
                                if (href && href != 'undefined' && href != '#')
                                    window.location.href = $(this).attr('href');
                                return false;
                            });
                        })
                        .end()
                        .show();
                    return false;
                }
            });

            return this;
        },
        'showPauseCommentForm': function () {
            if (this.model.get('started')) {

            }
        },
        'checkModel': function (callback, forced) {
            if (!this.model.get('full') || forced) {
                this.model.getFromServer(callback);
            } else {
                callback();
            }
        },
        'createTimer': function (time) {
            var timer = new PM_Timer(time);
            timer.container = this.$el.find('.js-time').get(0);
            return timer;
        },
        'showPauseDialog': function () {
            var t = this;
            t.$('.pause_dialog').show().find('textarea').trigger('focus');
            setTimeout(function () {
                t.$('.pause_dialog').one('clickoutside', function () {
                    $(this).hide();
                });
            }, 100);
            return false;
        },
        'showNextPopup': function (e) {
            var $target = $(e.currentTarget),
                $popup = $target.next();
            $popup.toggle();
            if ($popup.is(':visible')) {
                setTimeout(function () {
                    $popup.unbind('clickoutside').bind('clickoutside', function () {
                        $(this).hide()
                    });
                }, 10);
            }

            return false;
        },
        'changePlanTime': function (e) {
            var $target = $(e.currentTarget),
                time = $target.attr('rel'),
                obj = this,
                prop = $target.closest('[data-prop]').data('prop');

            if ($target.is('input')) {
                if (e.which === 13) {
                    time = parseInt($target.val());
                } else {
                    return;
                }
            }
            if (!time) {
                return this.editTask();
            }
            obj.model.set((prop || 'planTime'), time);
            obj.render();
            taskManager.SetTaskProperty(this.model.id, (prop || 'planTime'), time, function (data) {
				// obj.checkModel(function () {
				// }, true);
            });
            this.$el.find('[data-prop='+prop+'] .jsPlanTimeHolder').text(
                this.$el.find('.jsPlanTimeList:visible input"]').val()
            );
            this.$('.task-plantime > .dropdown > .dropdown-menu').hide();
            return false;
        },
        'loadResponsibleMenu': function () {
            var obj = this;
            $.get(this.options.responsibleMenuUrl, function (response) {
                $('body').append(response);
                obj.showResponsibleMenu();
            });
        },
        'bindResponsibleMenuEvents': function (userList, userInput, userItems) {
            var obj = this,
                unbindAndHideAll = function () {
                    userInput.val("").trigger('keyup.RespMenu');
                    userList.hide().unbind('.RespMenu').off('.RespMenuLive').unbind('clickoutside');
                    userList.find('.js-email-form').unbind('.RespMenu');
                    userList.find('.js-input-user-name').unbind('.RespMenu')
                },
                MAX_SYMBOLS_FOR_USERS_AJAX = 2;

            unbindAndHideAll();

            userList.on('click.RespMenuLive', 'a', function () {
                unbindAndHideAll();

                var uId = $(this).attr('rel');
                obj.changeResponsible(uId);
                return false;
            });

            userList.bind('clickoutside.RespMenu', function () {
                unbindAndHideAll();

                if (typeof obj.responsibleFailure === 'function') {
                    obj.responsibleFailure();
                }
                obj.responsibleMenuActive = false;
            });

            userList.find('.js-email-form').bind('submit.RespMenu', function () {
                unbindAndHideAll();

                var email = $(this).find('.js-email').val();
                obj.changeResponsible(email);
                return false;
            });

            userList.find('.js-input-user-name').bind('keyup.RespMenu', function () {
                var inputVal = $(this).val();
                if ($(this).data('timeout')) clearTimeout($(this).data('timeout'));
                $(this).data('timeout', setTimeout(function () {
                    if (inputVal.length > MAX_SYMBOLS_FOR_USERS_AJAX) {
                        $.ajax({
                            type: "POST",
                            data: {"action": "getUsers", "q": inputVal},
                            url: '/users_ajax/',
                            success: function (response) {
                                var data = $.parseJSON(response);
                                var mediaItems = [];

                                $('.js-user-list-of-user .js-get-rel').each(function () {
                                    mediaItems.push($(this).attr('rel'));
                                });

                                for (var i in data) {
                                    var avatar_type = '<div class="avatar_container js-avatar-container" rel=' + JSON.stringify(data[i].rel) + '></div>';
                                    if ($.inArray(data[i].id + '', mediaItems) == -1) {
                                        var $userLink = $('<a class="media-item js-get-rel" rel="' + data[i].id + '">' +
                                            '<span class="pull-left">' +
                                            avatar_type +
                                            '</span>' +
                                            '<div class="media-body">' +
                                            '<span class="user" onclick="document.location.href=\'/user_detail/?id=' + data[i].id + '\';event.stopPropagation();return false;">' + data[i].first_name + ' ' + data[i].last_name + '</span>' +
                                            '<span class="occupation"></span>' +
                                            '<div class="progress-bar-wrapper clearfix">' +
                                            '<div class="progress-bar-wrapper-title">Компетентность</div>' +
                                            '<div class="progress">' +
                                            '<div class="js-progress-success progress-bar progress-bar-success" style="width: 0%;"></div>' +
                                            '</div>' +
                                            '</div>' +
                                            '</div>' +
                                            '</a>');
                                        $('.add-user-list-of-users ul')
                                            .append($('<li class="media js-user-item ajaxAppend" style="display: list-item;"></li>')
                                                .append($userLink));
                                        obj.fillEffectivelyProgress($userLink, obj.model.id);
                                    }
                                }
                                $('.js-user-list-of-user .js-avatar-container').each(function () {
                                    $.updateAvatar(this, {size: 40});
                                });
                            }
                        });
                    } else {
                        userList.find('.ajaxAppend').remove();
                    }
                    userItems.each(function () {
                        var userItemVal = $(this).text();
                        var userItemIndexOf = userItemVal.toLowerCase().indexOf(inputVal.toLowerCase());
                        if (userItemIndexOf != -1) {
                            $(this).parents('.js-user-item').show();
                        } else {
                            $(this).parents('.js-user-item').hide();
                        }
                    });
                }, 200));

            });
        },
        'responsibleSuccess': function () {
            // console.log('success! id:' + this.model.id);
        },
        'responsibleFailure': function () {
            // console.log('failed! id:' + this.model.id);
        },
        'responsibleMenuActive': false,
        'showResponsibleArrow': function (userList) {
            var linkLeftPos = getObjectCenterPos(this.$('.js-select_resp')).left;

            var popupLeftPos = getObjectCenterPos(userList).left;
            var arrowPos = linkLeftPos - popupLeftPos;
            userList.find('.add-user-popup-top-arrow').css('left', arrowPos + 20); // approximately third letter of responsible name
        },
        'responsibleMenuPosition': function (userList) {
            var position = getObjectCenterPos(this.$('.js-select_resp')),
                left = position.left - 320 > 0 ? position.left - 320 : 0;
            userList.css({
                'position': 'absolute',
                'top': (position.top + position.height + 5),
                'left': left,
                'right': 'auto'
            });
        },
        'fillEffectivelyProgress': function (userLink, taskId) {
            var uId = $(userLink).attr('rel');
            var width = 0;
            if (typeof (taskRespSummary) == "undefined") {
                taskRespSummary = window.heliardData.taskRespSummary;
            }
            if (taskRespSummary[taskId] && taskRespSummary[taskId][uId])
                width = 100 * taskRespSummary[taskId][uId];
            $(userLink).find('.js-progress-success').css('width', width + '%');
        },
        'showResponsibleMenu': function () {
            var taskId = this.model.id;
            var obj = this;
            var userList = $('.js-add-user-popup');
            if (userList.length === 0) {
                this.loadResponsibleMenu();
                return false;
            }
            var userInput = userList.find('.js-input-user-name');
            var userItems = userList.find('.js-user-list-of-user .js-user-name');


            if (this.responsibleMenuActive) {
                if (userList.is(':visible') && parseInt(userList.attr('rel')) === taskId) {
                    userList.hide().unbind('.RespMenu').off('.RespMenuLive');
                    this.responsibleMenuActive = false;
                    return false;
                } else {
                    this.responsibleMenuActive = false;
                }
                return false;
            }
            this.bindResponsibleMenuEvents(userList, userInput, userItems);
            userList.attr('rel', taskId);
            this.responsibleMenuPosition(userList);
            userList.show();
            this.responsibleMenuActive = true;
            this.showResponsibleArrow(userList);
            userList.find('a').each(function () {
                obj.fillEffectivelyProgress(this, taskId);
            });

            if (userList.find('.js-add-user-popup .js-user-item').length > 9) {
                userList.find('.js-categories-list').css('display', 'table-cell');
            } else {
                userList.find('.js-categories-list').css('display', 'none');
            }


            userInput.focus();
            return false;
        },
        'responsibleApprove': function (e) {
            var uid = $(e.currentTarget).attr('rel');
            this.changeResponsible(uid);
            return false;
        },
        'stopAllTask': function () {
//            $('.Item.started a.taskPlayStop.stop').trigger('click');
        },
        'stopTaskViewWithoutServerSide': function (e) {
            this.taskStop(e, true);
            this.model.set({
                'started': false,
                'startedTimerExist': false
            });
            this.render();
        },
        'startTaskViewWithoutServerSide': function (e) {
            this.model.set({
                'started': true,
                'startedTimerExist': true
            });
            this.model.get('timer').start();
            this.render();
        },
        'taskStop': function (e, onlyView) {
            var comment = this.$('textarea[name=comment]').val();

            if (e && $(e.currentTarget).hasClass('pause_comment_cancel')) {
                this.$('textarea[name=comment]').val('');
                comment = '';
            } else if (!comment) {
                this.$('textarea[name=comment]').addClass('alert-error').one('keyup', function () {
                    $(this).removeClass('alert-error');
                    return false;
                });
                return false;
            }
            this.$('.js-task_play').removeClass('started');
            var obj = this;

            if (!onlyView)
                taskManager.TaskStop(this.model.id, {
                    'comment': comment,
                    'public': 1,
                    'solution': (this.$('input[name=solution]').is(':checked') ? 1 : 0)
                }, function (data) {
                    obj.model.set({
                        'started': false,
                        'startedTimerExist': false
                    });

                    if (obj.model.get('timer'))
                        obj.model.get('timer').stop();

                    if (window.mainTimer) {
                        window.mainTimer.stop();
                        if (CURRENT_TASK_VIEW) {
                            CURRENT_TASK_VIEW.stopTaskViewWithoutServerSide(e);
                        }
                    }
                    obj.$('.pause_dialog').hide();
                    obj.render();
                    userDynamics.getOpenTask();
                });

            return false;
        },
        'taskStart': function (e, onlyView) {
            if (this.model.get('started')) return false;

            var obj = this;
            if (!onlyView) {
                obj.stopAllTask();
                this.model.set('started', true);
                taskManager.TaskStart(this.model.id, function (data) {
                    data = $.parseJSON(data);

                    if (data.error) {
                        alert(data.error);
                        return false;
                    }

                    obj.$('.js-task_play').addClass('started');
                    obj.model.set({
                        'started': true,
                        'startedTimerExist': true,
                        'deadline': data.deadline
                    });

                    if (!obj.model.get('timer')) {
                        var timer = new PM_Timer({'container': obj.$('.js-time').get(0)});
                        $(timer.container).html(timer.toString());
                        obj.model.set('timer', timer);
                    }

                    obj.render();

                    obj.model.get('timer').start();

                    if (window.mainTimer) {
                        currentTaskInit(false, obj.model);
                        window.mainTimer.start();
                        if (CURRENT_TASK_VIEW) {
                            CURRENT_TASK_VIEW.startTaskViewWithoutServerSide(e);
                        }
                    }
                });
            }
            return false;
        },
        'openTask': function () {
            if (!this.model.get('closed')) return false;
            this.taskStop();

            var obj = this;
            taskManager.TaskOpen(this.model.id, function (data) {
                obj.model.set('closed', false);
                obj.render();
            });

            return false;
        },
        'closeTask': function () {
            if (this.model.get('closed')) return false;
            this.model.set('loader', true);
            this.render();
            this.taskStop();

            var obj = this;
            taskManager.TaskClose(this.model.id, function (data) {
                data = $.parseJSON(data);
                obj.model.set('loader', false);
                if (data.error) {
                    showError(data.error);
                    obj.render();
                } else {
                    obj.model.set('closed', data.closed);
                    obj.model.set('status', data.status);
                    obj.model.set('loader', false);
                    if (data.closed) {
                        $(window).trigger('task_closed', [data]);
                        obj.render();
                    } else {
                        obj.checkModel(function () {
                            obj.render();
                        });
                    }

                    obj.delegateEvents();
                }
            });

            return false;
        },
        'addToPlaning': function () {
            if (this.model.get('onPlanning')) return false;
            var obj = this;
            taskManager.AddToPlanning(this.model.id, function () {
                obj.model.set('onPlanning', true);
                obj.render();
            });
            return false;
        },
        'editTask': function () {
            document.location.href = '/task_edit/?id=' + this.model.id + '&backurl=' + (window.backurl ? window.backurl : "/");
        },
        'stopObserve': function () {
            var t = this;
            taskManager.simpleAction(this.model.id, 'stopObserve', function () {
                t.model.set({
                    'observer': false
                });
                t.render();
            });
        },
        'startObserve': function () {
            var t = this;
            taskManager.simpleAction(this.model.id, 'startObserve', function () {
                t.model.set({
                    'observer': true
                });
                t.render();
            });
        },
        'closePlanning': function () {
            if (!this.model.get('onPlanning')) return false;
            var obj = this;
            taskManager.RemoveFromPlanning(this.model.id, function () {
                obj.model.set('onPlanning', false);
                obj.render();
            });
            return false;
        },
        'approveTask': function () {
            var t = this;
            if (!t.model.get('resp') || !t.model.get('resp')[0] || !t.model.get('resp')[0]['name']) {
                alert('Подтвердить выполнение задачи можно только если выбран исполнитель.');
                return false;
            }
            this.setRevision();
            return true;
        },
        'setRevision': function () {
            var t = this;
            taskManager.SetTaskProperty(this.model.id, 'status', 'revision', function (data) {
                data = $.parseJSON(data);
                if (data.error)
                    showError(data.error);
                else {
                    t.model.set('status', 'revision');
                    t.render();
                }
            });
        },
        'removeTask': function () {
            if (confirm('Вы действительно хотите удалить эту расчет?')) {
                taskManager.deleteTask(this.model.id, function () {

                });

                if ('.js-subNum') {
                    var numSubStr = this.$el.parents('.visible-items').find('.js-subNum').text();
                    var numSub = parseFloat(numSubStr);
                    if (isNaN(numSub)) {
                        numSub = 0;
                    }
                    var newNumSub = numSub - 1;
                    if (newNumSub == 0) {
                        this.$el.parents('.visible-items').find('.js-subNum').text(' ');
                    } else {
                        this.$el.parents('.visible-items').find('.js-subNum').text(newNumSub + ' ');
                    }
                }

                this.model.destroy();
                if (!this.model.get('parent')) {
                    var $taskWrapper = this.$el.closest('.task-wrapper');
                    if ($taskWrapper.get(0)) {
                        $taskWrapper.remove();
                    } else {
                        this.$el.remove();
                    }
                }

                this.remove();
            }
        },
        'setReady': function () {
            var t = this;
            taskManager.SetTaskProperty(this.model.id, 'status', 'ready', function (data) {
                t.checkModel(function () {
                    t.model.set('status', 'ready');
                    t.render();
                });
            });
        },
        'baneUser': function () {
            var t = this;
            taskManager.BaneUser(this.model.id, function (data) {
                t.checkModel(function () {
                    t.model.set('resp', []);
                    t.render();
                });
            })
        },
        'toggleCritically': function () {
            var t = this, critically;

            if (this.model.get('critically') > CRITICALLY_THRESHOLD) {
                critically = 0.5;
            } else {
                critically = 0.95;
            }
            taskManager.SetTaskProperty(this.model.id, 'critically', critically, function (data) {
                t.checkModel(function () {
                    t.model.set('critically', critically);
                    t.render();
                });
            });
        },
        'addSubTask': function () {

        },
        'changeResponsible': function (uid) {
            var obj = this;
            taskManager.ChangeResponsible(this.model.id, uid, function (data) {
                if (data && data.resp) {
                    for (var k in data) {
                        obj.model.set(k, data[k]);
                    }
                    obj.responsibleSuccess();
                    obj.render();
                } else {
                    obj.responsibleFailure();
                }

            })
        },
        'initModal': function (url, callback) {
            var obj = this;
            $.get(url, function (data) {
                var html = data;
                html = html.replace('#TASK_NUMBER#', obj.model.get('number'));
                html = html.replace('#TASK_NAME#', obj.model.get('name'));

                $(html).on('shown.bs.modal', callback)
                    .on('hidden.bs.modal', function () {
                        $(this).modal('hide').remove();
                        $('.modal-backdrop').remove();
                    })
                    .modal('show');
            });
        },
        'setColor': function () {
            var obj = this;
            obj.initModal('/static/templates/color.html', function () {
                $('.js-color-block').click(function () {
                    $(this).activateListItem();
                }).filter('[data-color=' + obj.model.get('color') + ']').trigger('click');

                $('.js-save-color').click(function () {
                    var color = $('.js-color-block.active').data('color');
                    taskManager.SetTaskProperty(
                        obj.model.id,
                        'color',
                        color
                    );
                    obj.checkModel(function () {
                        obj.model.set('color', color);
                        obj.render();
                    });
                });
            });
        },
        'setDeadline': function () {
            var obj = this;
            taskManager.CheckEndTime(obj.model.get('planTime'), function (data) {
                data = $.parseJSON(data);
                if (data.endDate) {
                    var date = data.endDate.split(' ')[0],
                        time = data.endDate.split(' ')[1],
                        check = new Date(data.endDateForCheck.replace(' ', 'T')),
                        today = new Date();
                    today.setHours(23, 59, 59, 999);
                    var tomorrow = new Date(today.getTime() + 1000 * 60 * 60 * 24);

                    $('.js-deadlinedate').data('min-date', date).data('min-time', time);

                    if (check > today) {
                        $(".js-changeDeadlineDate[data-time*='today']").replaceWith("<span class='grey'><s>Сегодня</s></span>");
                        if (check > tomorrow) {
                            $(".js-changeDeadlineDate[data-time*='tomorrow']").replaceWith("<span class='grey'><s>Завтра</s></span>");
                        }
                    }
                }
            });

            $.get('/static/templates/deadline.html', function (data) {
                var html = data;
                html = html.replace('#TASK_NUMBER#', obj.model.get('number'));
                html = html.replace('#TASK_NAME#', obj.model.get('name'));

                $(html).on('shown.bs.modal', initPickers)
                    .on('hidden.bs.modal', function () {
                        $(this).modal('hide').remove();
                        $('.modal-backdrop').remove();
                    })
                    .modal('show');
            });

            var initPickers = function () {
                var curDeadline = obj.model.get('deadline'),
                    curReminder = obj.model.get('reminder'),
                    $deadline = $('.js-deadlinedate'),
                    $reminder = $('.js-reminderdate'),
                    dFinalDate;
                if (curDeadline) {
                    $deadline.val(curDeadline);
                    dFinalDate = moment(curDeadline, 'DD.MM.YYYY HH:mm');
                }
                if (curReminder) {
                    $reminder.val(curReminder)
                }

                $('.js-save_date').click(function () {
                    var deadline_date = $deadline.val(),
                        reminder_date = $reminder.val();
                    taskManager.SetDeadlineReminder(obj.model.id, deadline_date, reminder_date, function () {
                        obj.checkModel(function () {
                            obj.model.set('deadline', deadline_date);
                            obj.render();
                        });
                    });
                });

                var timeLogic = function (currentDateTime) {
                    var minDate = moment($deadline.data('min-date'), 'DD.MM.YYYY');
                    if (moment(currentDateTime).isSame(minDate, 'day')) {
                        this.setOptions({
                            minTime: $deadline.data('min-time')
                        });
                    } else
                        this.setOptions({
                            minTime: '00:00'
                        });
                };

                $deadline.add($reminder).datetimepicker({
                    'onShow': function (ct) {
                        timeLogic.call(this, ct);
                        this.setOptions({
                            minDate: $deadline.data('min-date')
                        });
                    },
                    'onChangeDateTime': timeLogic,
                    'onClose': function (ct, $i) {
                        if ($i.attr('name') == 'deadline_date') {
                            dFinalDate = moment(ct)
                        }
                    }
                });

                var changeDate = function (date, time) {
                    return moment(date).add(time, 'hours')
                };

                $('.js-changeDeadlineDate').click(function () {
                    var dDate;
                    var dThisDate = moment();
                    switch ($(this).attr('data-time')) {
                        case 'today':
                            var planTime = $(this).attr('default-time');
                            if (planTime) {
                                dFinalDate = changeDate(dThisDate, planTime);
                            } else {
                                dFinalDate = dThisDate;
                            }
                            break;
                        case 'tomorrow':
                            dFinalDate = changeDate(dThisDate, 24);
                            break;
                        case 'week':
                            dFinalDate = changeDate(dThisDate, 168);
                            break;
                    }
                    dDate = dFinalDate.format('DD.MM.YYYY HH:mm');
                    $deadline.val(dDate);
                    return false;
                });

                $('.js-changeReminderDate').click(function () {
                    var dDate;
                    var dRemindDate;
                    if (dFinalDate) {
                        switch ($(this).attr('data-time')) {
                            case 'hour':
                                dRemindDate = changeDate(dFinalDate, -1);
                                break;
                            case 'day':
                                dRemindDate = changeDate(dFinalDate, -24);
                                break;
                            case 'week':
                                dRemindDate = changeDate(dFinalDate, -168);
                                break;
                        }
                    }
                    dDate = dRemindDate.format('DD.MM.YYYY HH:mm');
                    $reminder.val(dDate);
                    return false;
                });
            }
        },
        'showMenu': function (e) {
            var arMenu = this.model.getMenuItems(),
                menuClass = 'task-menu',
                $taskMenu = $('<ul class="dropdown-menu pull-right text-left ' + menuClass + '"></ul>'),
                obj = this;
            $('.' + menuClass + '').remove();
            for (var i in arMenu) {
                var menuItem = arMenu[i],
                    $menuItem = $('<a></a>');
                (function (func) {
                    $menuItem
                        .append('<i class="fa fa-' + menuItem['icon'] + '"></i>&nbsp;&nbsp;')
                        .append(menuItem['itemText'])
                        .addClass(menuItem['itemClass'])
                        .attr('rel', menuItem['rel'])
                        .click(function () {
                            obj[func]();
                            $taskMenu.remove();
                            return false;
                        });
                    $('<li></li>').append($menuItem).appendTo($taskMenu);
                })(menuItem['itemMethod']);
            }

            $taskMenu.appendTo(this.$('.js-options_popup'))
                .show();
            $taskMenu.one('clickoutside', function () {
                $taskMenu.remove();
            });

            e.stopPropagation();
            return false;
        }
    });

    var taskAjaxManagerClass = function () {

    };

    taskAjaxManagerClass.prototype = {
        'ajaxUrl': '/task_handler',
        'taskAjaxRequest': function (data, callback, type) {
            return PM_AjaxPost(this.ajaxUrl, data, callback, type);
        },
        'TaskOpen': function (task_id, call) {
            if (!task_id) return false;
            this.taskAjaxRequest({
                'action': 'taskOpen',
                'id': task_id
            }, call);
            return this;
        },
        'TaskClose': function (task_id, call) {
            if (!task_id) return false;
            this.taskAjaxRequest({
                'action': 'taskClose',
                'id': task_id
            }, call);
            return this;
        },
        'simpleAction': function (task_id, action, call) {
            if (!task_id) return false;
            this.taskAjaxRequest({
                'action': action,
                'id': task_id
            }, call);
            return this;
        },
        'deleteTask': function (task_id, call) {
            if (!task_id) return false;
            this.taskAjaxRequest({
                'action': 'deleteTask',
                'id': task_id
            }, call);
            return this;
        },
        'TaskStart': function (task_id, call) {
            if (!task_id) return false;
            this.taskAjaxRequest({
                'action': 'taskPlay',
                'id': task_id,
                'play': task_id
            }, call);
            return this;
        },
        'TaskStop': function (task_id, addParams, call) {
            if (!task_id) return false;
            this.taskAjaxRequest(
                $.extend(addParams, {
                    'action': 'taskStop',
                    'id': task_id,
                    'pause': task_id
                }), call);
            return this;
        },
        'CreateTask': function (taskParams, parentTask, call) {
            if (!taskParams.taskname) return false;
            this.taskAjaxRequest({
                'action': 'fastCreate',
                'task_name': taskParams.taskname,
                'files': taskParams.files,
                'parent': parentTask
            }, call);
        },
        'SetTaskProperty': function (task_id, prop_code, val, call) {
            if (task_id && prop_code && val) {
                this.taskAjaxRequest({
                    'id': task_id,
                    'prop': prop_code,
                    'val': val
                }, call);
            }
        },
        'SetDeadlineReminder': function (task_id, deadline_date, reminder_date, call) {
            if (task_id) {
                this.taskAjaxRequest({
                    'id': task_id,
                    'prop': 'deadline',
                    'val': deadline_date,
                    'reminder': reminder_date
                }, call);
            }
        },
        'CheckEndTime': function (plan_time, call) {
            if (!plan_time) return false;
            this.taskAjaxRequest({
                'action': 'getEndTime',
                'plan_time': plan_time
            }, call);
            return this;
        },
        'AddToPlanning': function (id, call) {
            if (id) {
                this.taskAjaxRequest({
                    'id': id,
                    'prop': 'to_plan'
                }, call);
            }
        },
        'BaneUser': function (id, call) {
            if (id) {
                this.taskAjaxRequest({
                    'id': id,
                    'action': 'baneUser'
                }, call);
            }
        },
        'RemoveFromPlanning': function (id, call) {
            if (id) {
                this.taskAjaxRequest({
                    'id': id,
                    'prop': 'from_plan'
                }, call);
            }
        },
        'ChangeResponsible': function (id, uid, call) {
            if (!id) return false;
            if (!uid) return false;
            return this.taskAjaxRequest({
                'id': id,
                'resp': uid
            }, call, 'json');
        }
    };

    taskManager = new taskAjaxManagerClass();

    /**
     * создание на основе <div ..><a ... </a><a ... </a></div> моделей
     * поп-апов к input на основе введенных данных
     * @param input
     */
    var inputHintsManagerClass = function (input, tags, blocks) {
        this.$input = $(input);
        this.currentHint = false;
        this.inputText = '';
        //this.tags = tags;
        this.tags = {
            'Responsible': 'для ',
            'Date': ' до ',
            'Author': ' от ',
            'About': 'примерно '
        };
        //this.hintBlocks = blocks;
        this.hintBlocks = {
            'Responsible': $('#responsible_list'),
            'Date': $('#date_select_list'),
            'About': $('#deadline_select_list'),
            'Author': $('#author_list')
        };
        this.init();
    };

    inputHintsManagerClass.prototype = {
        'init': function () {
            var obj = this;
            obj.$input.keyup(function (e) {
                var key = getKeyPressed(e)
                    , tag = "", exist = false;
                obj.createCommand = '';
                for (var keytag in obj.tags) {
                    tag = obj.tags[keytag];

                    if ($(this).val().lastIndexOf(tag) != -1 && $(this).val().lastIndexOf(tag) == ($(this).val().length - tag.length)) {
                        obj.createCommand = tag;
                    }
                }

                if (e.ctrlKey && key == 32) { //ctrl+space
                    if (obj.createCommand)
                        obj.showHintByTag(this);
                } else if (e.ctrlKey && key == 78) { //ctrl+N
                    $('body,html').scrollTop(obj.$input.focus().offset().top);
                    return false;
                } else if (key == 40 && obj.currentHint.name) { //arrow down
                    obj.currentHint.container.find('a:visible').removeClass('selected').filter(':first').addClass('selected').focus();
                } else if (!e.ctrlKey && key != 13) {
                    obj.showHintByTag(this);
                }
            });

            for (var i in obj.hintBlocks) {
                obj.hintBlocks[i].keydown(function (e) {
                    var key = getKeyPressed(e);
                    if (obj.currentHint) {
                        if (key == 40) { //down
                            $(this).find('a.selected').removeClass('selected').next().addClass('selected').focus();
                            return false;
                        } else if (key == 38) { //up
                            $(this).find('a.selected').removeClass('selected').prev().addClass('selected').focus();
                            return false;
                        }
                    }
                });
            }
            for (var i in this.hintBlocks) {
                var block = this.hintBlocks[i];

                block.find('a').click(function () {
                    obj.pasteTag($(this).attr('rel'), i);
                    return false;
                });
            }
        },
        'showHint': function (hintName) {
            if (!hintName) return false;
            var hint_block = this.hintBlocks[hintName];
            var field = this.$input;
            var tags = this.tags;
            var obj = this;
            this.posDivToField(hint_block, field);

            this.inputText = '';

            $(field).unbind('keyup.' + hintName).bind('keyup.' + hintName, function (e) {
                var key = getKeyPressed(e);
                var lastFor = 0;
                if (lastFor = $(this).val().lastIndexOf(tags[hintName])) {
                    obj.inputText = $(this).val().substring((lastFor + tags[hintName].length), $(this).val().length);

                    var userLinks = obj.hintBlocks[hintName].find('a').show();

                    if (obj.inputText)
                        userLinks.not(":Contains('" + obj.inputText + "')").hide();

                    if (!userLinks.filter(":visible").get(0)) {
                        obj.hideHint()
                    }
                }
            });

            this.currentHint = {
                'name': hintName,
                'container': hint_block
            };
            return hint_block;
        },
        'posDivToField': function (block, field_selector) {
            if (!block) return false;
            var field = $(field_selector);
            if (typeof (block) == 'object') {
                block.show().appendTo(field.parent());
            }
        },
        'pasteTag': function (name, tag, new_val) {
            this.hideHint();
            /*var full_name = this.hintBlocks[tag].find('a[rel='+name+']').text();*/
            var inpval = this.$input.val();
            var pos = inpval.lastIndexOf(this.tags[tag]);

            pos += this.tags[tag].length;
            inpval = inpval.substring(0, pos);
            this.$input.val(
                inpval + "#" + (name == 'new' ? '' : name) + "#"
            ).focus();
            if (name == 'new') {
                var len = this.$input.val().length - 1;
                this.$input.get(0).setSelectionRange(len, len);
            }
            return false;
        },
        'hideHint': function () {
            if (this.currentHint.name) {
                this.currentHint.container.find('*').show().end().hide();
                this.$input.unbind('keyup.' + this.currentHint.name);
                this.currentHint = {}
            }
        },
        'showHintByTag': function (field) {
            if (!this.createCommand) return false;
            var currentTag = false;
            for (i in this.tags) {
                if (this.tags[i] == this.createCommand) {
                    currentTag = i;
                    break;
                }
            }
            if (currentTag) {
                this.showHint(currentTag, field);
            }
            /*else{
             this.hideHint();
             }*/
        }
    };

    $.fn.addTaskFilePasteSimple = function () {
        this.addFilePaste(function (data) {
            data = $.parseJSON(data);
            if (data && data.fid)
                $(this).val($(this).val() + ' файл #' + data.fid + '#').focus();
        });
        return this;
    }

})(jQuery);
