/**
 * Created with PyCharm.
 * User: Gvammer
 * Date: 18.10.12
 * Time: 14:44
 */
var widget_td;
$(function () {
    widget_td = new widgetObject({id: 'task_detail'});

    widget_td.state = {
        taskCreate: false,
        hintOpened: {
            'Responsible': false,
            'Date': false,
            'Author': false
        }
    };

    widget_td.task_id = arJSParams['taskId'];
    widget_td.TaskTimers = arTimers;
    widget_td.message_selector = '.js-taskMessage';
    widget_td.message_remove_selector = '.js-removeTaskMessage';
    widget_td.$container = $('#task_detail');
    widget_td.$task_holder = widget_td.$container.find('.subtask');
    widget_td.$messageList = widget_td.$container.find('.js-commentsContainer');
    widget_td.$userToSelect = false;
    widget_td.$createTaskInput = widget_td.$container.find('.js-addTaskInput input:text');
    widget_td.$blockAfterNewTask = widget_td.$task_holder.find('.js-addTaskInput');
    widget_td.$messageForm = widget_td.$container.find('form.newMessage');
    widget_td.$attachedFileContainer = widget_td.$container.find('.uploaded_file');
    widget_td.$todoList = widget_td.$container.find('.js-todo-list');
    widget_td.$todoContainer = widget_td.$container.find('.js-todo-container');
    widget_td.$filterTabs = widget_td.$container.find('.js-comments-filter-input');
    widget_td.$filterTabContainers = widget_td.$container.find('.js-container');
    widget_td.$todoTitle = widget_td.$container.find('.js-todo-title');
    widget_td.$bugList = widget_td.$container.find('.js-bug-list');
    widget_td.$addSubtaskBtn = widget_td.$container.find('.js-sub-tasks-button');
    widget_td.todoTpl = '<div class="warn-message">#TEXT##FILES_LIST#</button></div>';
    widget_td.subtasks = new window.taskList();
    widget_td.subtaskTemplates = {};

    widget_td.messageListHelper = new messageListManager(widget_td.$messageList, widget_td.task_id, task_detail_message_tpl);

    widget_td.subtaskTemplate = '<hr /><div id="taskLine_#TASK_ID#" data-taskid="#TASK_ID#" class="task clearfix">' +
        '<div class="span7 task-title">' +
        '<span class="task-name-wrapper"> #TASK_NAME# </span>' +
        '</div>' +
        '<div class="span2 task-responsibles">' +
        '<span class="dropdown">' +
        '<a href="" data-toggle="dropdown"></a>' +
        '</span>' +
        '</div>' +
        '<div class="span2 task-time">' +
        '<div class="inline task-timer">' +
        '<span class="dropdown">' +
        '<a class="Time" href="#" data-toggle="dropdown">#TIMER#</a>' +
        '</span>' +
        '</div>' +
        '<div class="inline task-plantime"> #PLAN_TIME# </div>' +
        '</div>' +
        '<div class="task-manage">' +

        '</div>' +
        '</div>';

    $.extend(widget_td, {
        'init': function () {
            var t = this;


            t.model = new window.taskClass(taskDetail);

            t.view = new window.taskViewClass({
                el: widget_td.$container.find('.widget-title').get(0),
                $el: widget_td.$container.find('.widget-title').eq(0),
                model: t.model
            });
            t.view.render = function () {
                if (this.model.get('closed')) {
                    this.$el.addClass('closed').find('.js-task_done').addClass('closed');
                } else {
                    this.$el.removeClass('closed').find('.js-task_done').removeClass('closed');
                }
                if (this.model.get('critically') > CRITICALLY_THRESHOLD) {
                    this.$el.addClass('danger');
                } else {
                    this.$el.removeClass('danger');
                }
                if (this.model.get('startedTimerExist')) {
                    this.$('.js-task_play').addClass('started').find('.fa').removeClass('fa-play-circle').addClass('fa-pause');
                } else {
                    this.$('.js-task_play').removeClass('started').find('.fa').addClass('fa-play-circle').removeClass('fa-pause');
                }

                //from tasks.js
                var $buttonClose = this.$('.js-task_done');
                var $approveBtn = this.$('.js-task_approve');
                if (this.model.get('subtasksQty')) {
                    $buttonClose.hide();
                    $approveBtn.hide();
                } else {
                    if (this.model.get('closed')) {
                        $buttonClose.hide();
                        $approveBtn.hide();
                    } else {
                        if (this.model.get('status') === 'not_approved') {
                            if (this.model.get('canApprove'))
                                $approveBtn.show();

                            $buttonClose.hide();
                        } else {
                            $approveBtn.hide();
                            $buttonClose.show();
                            var $closeIcon = $buttonClose.find('.fa');
                            if (this.model.get('canClose')) {
                                $closeIcon.removeClass('fa-check').addClass('fa-close');
                            } else {
                                $closeIcon.removeClass('fa-close').addClass('fa-check');
                            }
                        }
                    }
                }
                this.undelegateEvents();
                this.delegateEvents();
            };
            t.view.render();
//            baseConnector.addListener('connect', function(){
//
//                    t.view.checkModel(function(){
//                        t.view.render();
//                    }, true);
//
//            });

            $('.js-need-time').click(function () {
                var $hoursInput = $('.js-need-time-hours');
                if ($(this).is(':checked')) {
                    $hoursInput.show();
                } else {
                    $hoursInput.hide();
                }
            });

            $('.sendTaskMessage').on("click", function () {
                var closeTask = $(this).hasClass('btn-close'),
                    btn = this,
                    actions = false,
                    parForm = $(this).closest("form.newMessage"),
                    getTextarea = parForm.find("textarea"),
                    getCheckboxs = parForm.find("input[type=checkbox]"),
                    searchLoadBufPhotos = parForm.find("input[name=files]");


                if (getTextarea.val() != '') actions = true; //Проверка Textarea
                /*getCheckboxs.each(function(){ //Проверка Checkbox'ы
                 if($(this).prop("checked")) actions = true;
                 });*/
                if (searchLoadBufPhotos.length) actions = true; //Проверка закрепленных из буфера фотографии

                if (actions) {
                    if (!$(btn).pushed()) {
                        if (closeTask) {
                            $(btn).parent().find('[name=close]').val('Y');
                        }

                        $(btn).pushTheButton();
                        widget_td.newMessage(function (data) {
                            $(btn).pullTheButton();
                            widget_td.renderFileList();
                        });
                    }
                    getTextarea.closest(".form-group.has-error").removeClass("has-error");
                } else getTextarea.focus().closest(".form-group").addClass("has-error");

                return false;
            });

            //Отслеживать ctrl+enter
            $(document).keydown(function (event) {
                if (event.which == 13 && (event.ctrlKey || event.metaKey)) {
                    $('.sendTaskMessage:not(.btn-close, .js-change_resp)').click();
                    return false;
                }
            });

            widget_td.$addSubtaskBtn.click(function () {
                $(".js-addTaskInput").toggle().not(':hidden').focus();
                return false;
            });

            widget_td.$container.on("keypress", "form.newMessage .combobox-container .combobox", function (e) {
                if (e.which == 13) {
                    $('.sendTaskMessage:not(.btn-close)').click();
                    $("form.newMessage").submit(function () {
                        return false;
                    });
                    return false;
                }
            });

            widget_td.$container.on('click', '.js-ShowClosedSubtasks', function () {
                var proc, h = 'hidden';
                if ($(this).data('open')) {
                    proc = function (view) {
                        return view.$el.addClass(h).prev('hr').addClass(h);
                    };
                    $(this).data('open', false).text('Показать закрытые задачи');
                } else {
                    proc = function (view) {
                        return view.$el.removeClass(h).prev('hr').removeClass(h);
                    };
                    $(this).data('open', true).text('Скрыть закрытые подзадачи');
                }
                for (var i in widget_td.subtaskTemplates) {
                    var view = widget_td.subtaskTemplates[i];
                    if (view.model.get('closed')) {
                        proc(view);
                    }
                }
                return false;
            });

            widget_td.$filterTabs.click(function () {
                var type = $(this).val();
                widget_td.$filterTabContainers.hide().filter('[data-type=' + $(this).val() + ']').show();
            });


            var task;
            for (var i in aSubTasks) {
                task = new window.taskClass(aSubTasks[i]);
                widget_td.subtasks.add(task);
            }

            widget_td.subtasks.each(function (task) {
                var view = new window.taskViewClass({'model': task});
                view.createEl().render();

                widget_td.addTaskElementAndHr(view.$el);

                if (view.model.get('closed')) {
                    view.$el.addClass('hidden').prev('hr').addClass('hidden');
                }
                widget_td.subtaskTemplates[task.id] = view;
            });

            this.subtasks.on('add', function (task) {

            });

            widget_td.messageListHelper.addMessages(arJSParams.messages);

            baseConnector.addListener('fs.comment.add', function (data) {
                if (data && data.task) {
                    if (data.task.id == widget_td.task_id) {
                        widget_td.messageListHelper.addMessages([data]);
                        widget_td.renderFileList();
                    }
                }
            });

            if (arTimers)
                for (var i in arTimers) {
                    if (widget_td.subtaskTemplates[i])
                        arTimers[i].container = $('#taskLine_' + i + ' .js-time');
                    $(arTimers[i].container).html(arTimers[i].toString());
                }

            widget_td.$createTaskInput.enterPressed(function (e) {
                widget_td.CreateSubTask();
                return false;
            });

            widget_td.$messageForm.find('textarea[name=task_message]').addFilePaste(function (data) {
                data = $.parseJSON(data);
                console.log(data);
                if (data && data.fid) {
                    widget_td.$attachedFileContainer.show()
                        .append($attachedFileBlock(data.path, data.fid, data.fid, data.type, data.thumbnail));
                }
            });

            widget_td.removeTempScripts();
            baseConnector.addListener('fs.task.update', function (data) {
                if (data.id == widget_td.model.id) {
                    widget_td.model.set(data);
                    widget_td.view.render();
                }
            });

            widget_td.$messageList.on('click', '.js-quote', function () {
                var model = widget_td.messageListHelper.getById($(this).attr('rel'));
                var text = model.get('text').replace(new RegExp(/\[Q\]([^]+)\[\/Q\]/mig), '');
                widget_td.quote(text);
                var selData = widget_td.$userToSelect.data('combobox').map;
                for (var i in selData) {
                    if (selData[i] == $(this).data('author')) {
                        widget_td.$messageForm.find('input:text.combobox').val(i);
                    }
                }
                widget_td.$messageForm.find('[name=to]').val($(this).data('author'));
                return false;
            });

            widget_td.$messageList.on('click', '.js-reply', function () {
                var selData = widget_td.$userToSelect.data('combobox').map;
                var isHidden = $(this).data('hidden'), checked;
                if (isHidden) {
                    checked = 'checked';
                } else {
                    checked = false;
                }
                $('input[name=hidden]').attr('checked', checked);
                for (var i in selData) {
                    if (selData[i] == $(this).attr('rel')) {
                        widget_td.$messageForm.find('input:text.combobox').val(i);
                    }
                }
                widget_td.$messageForm.find('[name=to]').val($(this).attr('rel'));
                widget_td.$messageForm.find('textarea').focus();
                return false;
            });

            //widget_td.$todoContainer.on('click', '.js-todo-checkbox .js-checkbox, .js-bug-checkbox .js-checkbox', function () {
            //    widget_td.messageListHelper.getById($(this).attr('rel')).view.checkTodo();
            //    return false;
            //});

            widget_td.$userToSelect = $('.combobox').combobox();

            widget_td.renderTodo();
            widget_td.renderFileList();
        },
        'renderFileList': function () {
            return;
            var $fileList = $('.js-file-list'),
                filesQty = 0,
                fileTpl = '<div class="js-file-row message margin-bottom-20">' +
                    '           <div class="avatar"><img class="js-file-icon"></div>' +
                        '       <div class="message-content">' +
                        '           <div class="message-info"> ' +
                        '               <span class="js-date message-info-time"></span>' +
                        '           </div>' +
                        '           <div class="message-desc">' +
                        '               <a class="task-file--name js-file-name"></a>' +
                        '           </div>' +
                        '       </div>' +
                    '       </div>';

            widget_td.messageListHelper.forEachBack(function (model) {
                if (model.get('files')) {
                    model.get('files').forEach(function (file) {
                        if (!$fileList.find('[rel='+file.id+']').size()) {
                            var $el = $(fileTpl).attr('rel', file.id);
                            var $link = $el.find('.js-file-name').text(file.name);
                            if (file.viewUrl || file.is_picture) {
                                $link.attr('href', file.is_picture ? file.url : file.viewUrl).addClass(file.is_picture ? 'fnc' : 'fnc_ajax');
                            } else {
                                $link.attr('href', file.url).attr('target', '_blank');
                            }

                            var pictTpl = '';
                            if (file.is_picture) {
                                pictTpl = '<a class="fnc task-file--thumbnail" href="' + file.url + '"><img class="media-object img-thumbnail" src="' + file.thumb100pxUrl + '" /></a>';
                            } else {
                                var iconClass = getIconForExtension(file.type);
                                pictTpl = '<a class="uploaded_file-item fnc task-file--thumbnail" style="margin:0 10px;" href="' + file.url + '"><span class="uploaded_file-item-image"><i class="fa fa-file' + (iconClass ? '-' + iconClass : '') + '-o"></i></span></a>';
                            }
                            $el.find('.js-file-icon').replaceWith(pictTpl);
                            $el.find('.js-date').text(file.date_create);
                            $fileList.prepend($el);
                        }

                        filesQty++;
                    });
                }
            });

            $('.js-files-exist').text(filesQty);
        },
        'renderTodo': function () {
            var roQty = 0, soQty = 0, eoQty = 0;
            widget_td.messageListHelper.forEachBack(function (model) {
                if (model.get('type')) {
                    if (model.get('type') == 'ro') {
                        roQty++;
                    }
                    if (model.get('type') == 'so') {
                        soQty++;
                    }
                    if (model.get('type') == 'eo') {
                        eoQty++;
                    }
                    //var $el = widget_td.$todoList.find('.js-todo-checkbox[rel=' + model.id + ']').eq(0);
                    if (model.$todoView && model.$todoView.size()) {
                        model.$todoView.show();
                    } else {
                        var tpl = widget_td.todoTpl.replace('#ID#', model.id)
                            .replace('#TEXT#', model.get('text'));


                        var aFiles = model.view.getFilesHtml();
                        var $pictures = $('<div class="message-pictures clearfix"></div>'),
                            $otherFiles = $('<div class="message-other-files clearfix"></div>'),
                            $filesListblock = $('<div class="message-files-list-block clearfix"></div>'),
                            exist, i;

                        if (aFiles['pictures']) {
                            exist = false;
                            for (i in aFiles['pictures']) {
                                exist = true;
                                if (aFiles['pictures'].hasOwnProperty(i))
                                    $pictures.append(aFiles['pictures'][i]);
                            }
                            if (exist)
                                $filesListblock.append($pictures);
                        }

                        if (aFiles['other']) {
                            exist = false;
                            for (i in aFiles['other']) {
                                exist = true;
                                if (aFiles['other'].hasOwnProperty(i))
                                    $otherFiles.append(aFiles['other'][i]);
                            }
                            if (exist)
                                $filesListblock.append($otherFiles);
                        }
                        tpl = tpl.replace('#FILES_LIST#', $filesListblock.get(0).innerHTML);

                        model.$todoView = $(tpl);
                        model.$todoView.prependTo($('.js-'+model.get('type')+'Container'));
                        model.$todoView.find('.js-checkbox').click(function () {
                            model.view.$el.find('.js-check-todo, .js-check-bug').trigger('click');
                        });
                    }


                    if (model.get('checked')) {
                        model.$todoView.find('.fa').removeClass('fa-square-o').addClass('fa-check-square-o');
                    } else {
                        model.$todoView.find('.fa').addClass('fa-square-o').removeClass('fa-check-square-o');
                    }
                }
            });
            widget_td.$filterTabs.filter('[value=ro]').closest('.js-tab')
                .find('.js-exist').html(roQty);

            widget_td.$filterTabs.filter('[value=so]').closest('.js-tab')
                .find('.js-exist').html(soQty);

            widget_td.$filterTabs.filter('[value=eo]').closest('.js-tab')
                .find('.js-exist').html(eoQty);
        },
        'quote': function (text) {
            if (text) {
                var nText = "";
                text = '[Q]' + text.trim() + '[/Q]';
                var $txtarea = widget_td.$messageForm.find('textarea[name=task_message]');
                nText = $txtarea.val().trim();
                if (nText) {
                    nText = nText + '\r\n';
                }
                $txtarea.val(nText + text + "\r\n").focus();
            }
        },
        'removeTempScripts': function () {
            $('.temp_scripts').remove();
        },
        'removeMessage': function (id) {
            return this.removeMessageRequest(id, function (data) {
                if (data.success == "Y")
                    $(widget_td.message_selector).filter('[data-id=' + id + ']').remove();
            });
        },
        'removeMessageRequest': function (id, callback) {
            return PM_AjaxPost(
                '/task_handler',
                {
                    'action': 'removeMessage',
                    'id': id
                },
                callback,
                'json'
            );
        },
        'newMessage': function (callback) {
            if (widget_td.task_id) {
//                var text = widget_td.$messageForm.find('textarea[name=task_message]').val();
                widget_td.$messageForm.ajaxSubmit({
                    'success': function (data) {
                        data = $.parseJSON(data);
                        data['noveltyMark'] = true;
                        widget_td.messageListHelper.addMessages([data]);
                        widget_td.$messageForm.find('textarea[name=task_message], [name="need-time-hours"]').val('')
                            .closest('.newMessage').removeClass('active');
                        widget_td.$messageForm.find('.js-need-time:checked').trigger('click');
                        widget_td.$messageForm.find('.js-solution-set:checked').trigger('click');
                        widget_td.$messageForm.find('[name=files]').remove();
                        widget_td.$attachedFileContainer.empty();
                        if (callback) callback(data);
                    }
                });
            }
        },
        'CreateTaskRow': function (oTaskData) {
            if (!oTaskData.id) return false;
            var model = new window.taskClass(oTaskData);
            var view = new window.taskViewClass({model: model});
            view.createEl().render();
            this.addTaskElementAndHr(view.$el);
            return view.$el;
        },
        'addTaskElementAndHr': function ($el) {
            $($el).insertBefore(this.$blockAfterNewTask);
//            if ($el.prev().get(0))
//                $('<hr />').insertBefore($el);TODO: проставлять класс first
        },
        'CreateSubTask': function (taskname) {
            if (!taskname) taskname = widget_td.$createTaskInput.val();
            if (!taskname) return false;

            taskManager.CreateTask({'taskname': taskname}, widget_td.task_id, function (data) {
                var data = $.parseJSON(data);
                alert('mess')
                console.log(data)
                if (data.parent != widget_td.task_id) {
                    document.location.href = '/task_detail/?id=' + data.parent;
                    return;
                }

                if (data.name) {
                    widget_td.$createTaskInput.val('');
                    var $taskRow = widget_td.CreateTaskRow(data, widget_td.task_id);

                    if ($taskRow) {
                        arTimers[data.id] = new PM_Timer();
                        arTimers[data.id].container = $taskRow.find('.Time').eq(0);

                        arTimers[data.id].container.html(arTimers[data.id].toString());
                    }
                }
                a = window.location.href
                window.location.href = "/task_edit/?id=" + data.id + "&backurl=/";
            });
            return this;
        }
    });
    widget_td.messageListHelper.reversed = true;
    widget_td.init();

    document.mainController.widgetsData["task_detail"] = widget_td;

    $(window)
        .bind('pmCheckTodo', function (e, model) {
            //if (model.get('bug')) {
            //    var place = "bug"
            //}
            //if (model.get('todo')) {
            //    var place = "todo"
            //}
            var $checkbox = $('.js-todo-checkbox[rel=' + model.id + '] .fa');
            var rem = 'removeClass', add = 'addClass';

            if (model.get('checked')) {
                rem = 'addClass';
                add = 'removeClass';
            }

            $checkbox[rem]('fa-check-square-o')[add]('fa-square-o');
            widget_td.renderTodo();
        })
        .bind('pmSetTodo', function (e, model) {
            //function strip(html) {
            //    var tmp = document.createElement("DIV");
            //    tmp.innerHTML = html;
            //    return tmp.textContent || tmp.innerText || "";
            //}

            //if (model.get('bug')) {
            //    var place = "bug"
            //}
            //if (model.get('todo')) {
            //    var place = "todo"
            //}
            var $checkbox = $('.js-todo-checkbox[rel=' + model.id + ']');
            if ($checkbox.size()) {
                $checkbox.hide();
            }
            widget_td.renderTodo();
            //if ($checkbox.get(0)) {
            //    return false;
            //}
            //$checkbox = $('<button data-placement="top" data-toggle="popover" data-container="body" class="js-'
            //    + place + '-checkbox" type="button" data-original-title="" title=""></button>')
            //    .attr('rel', model.id)
            //    .attr('data-content', strip(model.get('text')));
            //var $i = $('<i></i>');
            //if (model.get('checked')) {
            //    $i.addClass('fa fa-square-check-o');
            //} else {
            //    $i.addClass('fa fa-square-o');
            //}
            //var list;
            //switch (place) {
            //    case "todo":
            //        list = widget_td.$todoList;
            //        break;
            //    case "bug":
            //        list = widget_td.$bugList;
            //        break;
            //}
            //
            //$checkbox.append($i).appendTo(list).popover({
            //    'trigger': 'hover'
            //});
            //widget_td.$todoContainer.removeClass('hidden');
            //widget_td.$todoTitle.removeClass('hidden');

        });

    $('[data-toggle="popover"]').popover({
        'trigger': 'hover'
    });

    $('textarea[name=task_message]').keyup(function () {
        if (!$(this).val())
            $(this).closest('.newMessage').removeClass('active');
        else
            $(this).closest('.newMessage').addClass('active');
    });

    $('.js-add-subtask-helper').click(function () {
        $('.js-add-subtask-input').removeClass('hidden').focus();
        $(this).remove();
        return false;
    });

    taskFileUpload(
        function (event, id, filename, data) {
            if (data.id) {
                $attachedFileBlock(data.src, data.name, data.id, data.type, data.thumbnail).appendTo(widget_td.$attachedFileContainer.show());
                $(this).fineUploader('setDeleteFileParams', {"file_id": data.id}, id);
            }
        },
        false,
        true
    );

    $('.js-est-tabs').click(function () {
        $('.js-est-tabs').removeClass('active');
        $(this).addClass('active');
        $('.js-tab-ext').hide();
        $('.js-tab-ext[data-tab="'+$(this).data('tab')+'"]').show();
        return false;
    });
});