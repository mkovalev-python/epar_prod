/**
 * Created with PyCharm.
 * User: Gvammer
 * Date: 29.01.14
 * Time: 9:21
 */
var mytaskViewClass;
var currentTaskInit = function(data, model){
    var currentTask;
    if (model)
        currentTask = model;
    else
        currentTask = new window.taskClass(data);

    if (CURRENT_TASK_VIEW) {
        CURRENT_TASK_VIEW.model = currentTask;
    } else {
        CURRENT_TASK_VIEW = new mytaskViewClass({
            model: currentTask,
            el: $('.js-currentTask')
        });
    }

    if (oMyCurrentTimer && !model)
        currentTask.set('timer', oMyCurrentTimer);

    if (!currentTask.get('name')){
        currentTask.getFromServer(function(){
            CURRENT_TASK_VIEW.render();
        });
    }
    CURRENT_TASK_VIEW.render();
    return currentTask;
}

if (window.taskViewClass)
    mytaskViewClass  = window.taskViewClass.extend({
        events: {
            "click a.js-stop-timer"        : "currentTimerStop",
            "click a.js-cancel-timer"      : "currentTimerStop",
            "click .js-mainTimer, .js-play": "showTimerMainPopup"
        },
        currentTimerStop: function(e){
            this.taskStop(e);
            if (window.widget_tl && widget_tl.TL_TaskTemplates[this.model.id]){
                var taskView = widget_tl.TL_TaskTemplates[this.model.id];
                taskView.model.get('timer').stop();
                taskView.stopTaskViewWithoutServerSide(e);
            }
        },
        render: function(){
            var t = this,
                fpl = 'fa-play-circle',
                fps = 'fa-pause',
                $playbtn = t.$('.js-play'),
                $onlystrtd = t.$('.js-onlystarted');
            if (t.model.get('started')){
                $playbtn.removeClass(fpl).addClass(fps);
                $onlystrtd.show();
            } else {
                $playbtn.addClass(fpl).removeClass(fps);
                $onlystrtd.hide();
            }
            if (t.model.get('project'))
                t.$('.js-projectName').html(t.model.get('project')['name']);
            if (t.model.get('parentTask') && t.model.get('parentTask')['name']){
                t.$('.js-parentTaskName').html(t.model.get('parentTask')['name']);
                t.$('.js-taskName').html(t.model.get('name'));
            }else{
                t.$('.js-parentTaskName').html(t.model.get('name'));
            }
            t.$('.js-description').html(t.model.get('text'));
        },
        showTimerMainPopup: function(e){
            var t = this;

            this.$('.js-mainTimerPopup').show().find('textarea').trigger('focus').unbind('click.mainTimer')
                    .bind('click.mainTimer', function(e){
                e.stopPropagation();
            });

            //.js-mainTimerPopup clickoutside
            $(document).unbind('click.mainTimer')
                    .bind('click.mainTimer', function(){
                t.$('.js-mainTimerPopup').hide();
            });

            e.stopPropagation();
        }
    });
$(function(){
    if (oMyCurrentTimer){
        oMyCurrentTimer.container = $('.js-mainTimer');

        window.mainTimer = (function(){
            this.$elem = $('.js-currentTask .js-play');
            this.timer = oMyCurrentTimer;

            this.start = function(){
                this.$elem.removeClass('fa-play-circle').addClass('fa-pause');
                this.timer.start();

                return this;
            }

            this.stop = function(){
                this.$elem.removeClass('fa-pause').addClass('fa-play-circle');
                this.timer.stop();
                if (CURRENT_TASK_VIEW) {
                    CURRENT_TASK_VIEW.taskStop(false, true);
                }
                return this;
            }

            var t = this;
            baseConnector.addListener('fs.task.update',function(data){
                    if (data && data.id){
                        if (!CURRENT_TASK_VIEW || data.started === true){
                            if (data.eventAuthor && data.eventAuthor == window.baseUserParams.userId) {
                                if (window.widget_tl && window.widget_tl.TL_TaskTemplates[data.id]){
                                    currentTaskInit(data, widget_tl.TL_TaskTemplates[data.id].model);
                                }else{
                                    currentTaskInit(data);
                                }
                            }
                        }
                        if (CURRENT_TASK_VIEW && CURRENT_TASK_VIEW.model.id == data.id){
                            for (var k in data){
                                CURRENT_TASK_VIEW.model.set(k, data[k]);
                            }

                            if (data.started === true){
                                t.start();
                            }else if (data.started === false){
                                if (CURRENT_TASK_VIEW.model.get('started'))
                                    t.stop();
                            }

                            CURRENT_TASK_VIEW.render();
                        }
                    }
                });

            return this;
        })();

        baseConnector.addListener('disconnect', function(){
            if (!window.unloadPage) {
//                alert('disconnect');
                window.disconnectTimeout = setTimeout(function(){
                    if (oMyCurrentTimer && oMyCurrentTimer.started) {
                        window.mainTimer.stop();
                        oMyCurrentTimer.started = false;
                        alert('Произошло отключение от сервера. Обновите страницу.');
                    }

                }, 20000);
            }
        });
        baseConnector.addListener('connect', function(){
            if (window.disconnectTimeout) {
                clearTimeout(window.disconnectTimeout);
            }
        });
    }

    if (CURRENT_TASK_DATA)
        currentTaskInit(CURRENT_TASK_DATA);
});
