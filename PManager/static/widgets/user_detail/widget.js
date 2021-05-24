/**
 * Created with PyCharm.
 * User: Gvammer
 * Date: 18.10.12
 * Time: 14:44
 */

$(function () {
	$('.user-prizes-slider').bxSlider({
		slideWidth: 150,
		minSlides: 3,
		maxSlides: 3,
		controls:true,
        autoControls:false,
		pager:false,
        hideControlOnEnd:true,
        infiniteLoop:false,
		mode:'horizontal',
		auto:true,
		pause:5000,
        nextText:'<i class="fa fa-angle-right"></i>',
        prevText:'<i class="fa fa-angle-left"></i>'
	});

    var widget_ud = new widgetObject({id: 'user_detail'});
    widget_ud.state = {
        taskCreate: false,
        hintOpened: {
            'Responsible': false,
            'Date': false,
            'Author': false
        }
    };

    widget_ud.templateUrl = "/static/item_templates/tasklist/task.html";
    widget_ud.container = $('#user_detail');
    widget_ud.user_id = global_user_id;
    widget_ud.userInfoSelector = '.userInfo';
    widget_ud.taskList = new window.taskList();
    widget_ud.taskListObservers = new window.taskList();
    widget_ud.taskTemplates = {};
    widget_ud.$taskContainer = $('.js-tasks');
    widget_ud.$taskContainerObservers = $('.js-tasks-observers');

    $.extend(widget_ud, {
        'init': function () {
            this.$userInfoBlock = this.container.find(this.userInfoSelector);
            var oTask;
            for (var i in aTaskList) {
                aTaskList[i]['is_responsible_list'] = true;
                oTask = new window.taskClass(aTaskList[i]);
                widget_ud.taskList.add(oTask);
            }
//            for (var i in aTaskListObservers){
//                oTask = widget_ud.taskList.get(aTaskListObservers[i]['id']);
//                if (oTask) {
//                    oTask.set('is_observer_list', true);
//                }else{
//                    aTaskListObservers[i]['is_observer_list'] = true;
//                    oTask =  new window.taskClass(aTaskListObservers[i]);
//                    widget_ud.taskList.add(oTask);
//                }
//            }
            this.addOnlineStatusListeners();
            widget_ud.taskList.each(function (task) {
                if (task.get('is_observer_list')) {
                    widget_ud.addTaskLine(task.toJSON(), widget_ud.$taskContainerObservers);
                }
                if (task.get('is_responsible_list')) {
                    widget_ud.addTaskLine(task.toJSON(), widget_ud.$taskContainer);
                }
            });
            widget_ud.taskListObservers.each(function (task) {
                widget_ud.addTaskLine(task.toJSON(), widget_ud.$taskContainerObservers);
            });
            $('.js-delete-user').click(function () {
                return confirm('Вы действительно хотите удалить данного пользователя?');
            });
            $('.js-role-check').click(function () {
                PM_AjaxPost(
                    '/users_ajax/',
                    {
                        'action': 'setRole',
                        'role': $(this).data('name'),
                        'roleProject': $(this).data('project'),
                        'user': $(this).data('user-id'),
                        'set': ($(this).is(':checked') ? 1 : 0)
                    },
                    function (data) {
//                        alert(data);
                    }
                )
            });
            dashboard('#dashboard', USER_TIME_DATA);

            initSpecialtiesFind(function($t, appendSkills) {
                    PM_AjaxPost(
                        '/users_ajax/',
                        {
                            'action': 'addSpecialty',
                            'specialty': $t.val(),
                            'user': $t.data('user-id')
                        },
                        function (response) {
                            if (response == 'already has this specialty') {
                                $t.val('');
                            } else {
                                var data = $.parseJSON(response);
                                appendSkills(data['id'], data['name']);
                                $t.val('');
                            }
                            $searchDropdown.hide();
                        }
                    );
                }, function($t) {
                    PM_AjaxPost(
                        '/users_ajax/',
                        {
                            'action': 'deleteSpecialty',
                            'specialty': $t.data('specialty'),
                            'user': $('.js-save_specialty').data('user-id')
                        },
                        function () {
                            $t.closest('.js-skill-item').remove();
                        }
                    )
                });
        },
        'addTaskLine': function (taskData, $container) {
            var task = widget_ud.taskList.get(taskData.id);
            var view = new window.taskViewClass({'model': task});

            widget_ud.taskTemplates[task.id] = view;
            view.createEl().render();

            var $task_el = $('<div></div>').addClass('task-wrapper')
                .append(view.$el)
                .append('<div class="subtask"></div>');
            $container.append($task_el);
            view.$('.js-select_resp, .add-subtask').each(function () {
                $(this).replaceWith($('<strong></strong>').append($(this).find('.fa-plus').remove().end().html()));
            });
            view.delegateEvents();
        },
        'addOnlineStatusListeners': function () {
            baseConnector.addListener('connect', function () {
                if (widget_ud.statusInterval) clearInterval(widget_ud.statusInterval);
                widget_ud.setOnlineStatusFromServer();
                widget_ud.statusInterval = setInterval(function () {
                    widget_ud.setOnlineStatusFromServer();
                }, 5000)
            });

            baseConnector.addListener('userLogin', function (userData) {
                if (userData.id == widget_ud.user_id) {
                    widget_ud.setUserStatus('online');
                }
            });
        },
        "setOnlineStatusFromServer": function () {
            baseConnector.addListener('users:data', function (userData) {
                userData = $.parseJSON(userData);
                widget_ud.setUserStatus(userData['status']);
            });
            baseConnector.send("users:get_user_data", {
                'id': this.user_id
            });
        },
        'setUserStatus': function (status) {
            if (status)
                this.$userInfoBlock.attr('data-status', status);
        }
    });

    widget_ud.init();

    document.mainController.widgetsData["user_detail"] = widget_ud;
    var hash = window.location.hash;
    hash && $('ul.nav a[href="' + hash + '"]').tab('show');

    $('#myTab a').bind(function (e) {
        e.preventDefault();
        $(this).tab('show');
        window.location.hash = this.hash;
        return false;
    });

    $('.js-link-tasks').click(
        function() {
            $('.js-current-tasks').trigger('click');
        }
    );

    $('.js-add-project').click(
        function() {
            $('.js-tab-menu > li').removeClass('active')
        }
    );

    $('.js-show-bonuses').click(function(){
        $('.js-bonuses, .js-productivity').toggle();
        $('[href="#svodka"]').trigger('click');
        return false;
    });

    $('.js-pay').click(function() {
        var t = this;
        if (confirm('Вы действительно хотите списать эту сумму?')) {
            var data = {
                    action: 'send_payment',
                    role: $(t).data('role'),
                    sum: -Math.round($(t).data('sum')),
                    comment: ''
                };
            PM_AjaxPost(
                '/project/'+$(t).data('project')+'/',
                data,
                function (data) {
                    if (data['result']) {
                        $(t).closest('.js-pay-item').remove();
                        if (!$('.js-pay-item').get(0)) {
                            $('.js-show-bonuses').trigger('click').remove();
                        }
                    }
                },
                'json'
            );
        }
        return false;
    });
});

function dashboard(id, fData) {
    var randomScalingFactor = function(){ return Math.round(Math.random()*100)}, i, labels = [], datasets = [[],[],[]];
    for (i in fData) {
        labels.push(fData[i]['State']);
        datasets[0].push(fData[i]['freq']['time']);
        datasets[1].push(fData[i]['freq']['tasks']);
        datasets[2].push(fData[i]['freq']['commits']);
    }
    var barChartData = {
		labels : labels,
		datasets : [
			{
				fillColor : "rgba(220,220,220,0.5)",
				strokeColor : "rgba(220,220,220,0.8)",
				highlightFill: "rgba(220,220,220,0.75)",
				highlightStroke: "rgba(220,220,220,1)",
				data : datasets[0]
			},
			{
				fillColor : "rgba(151,205,187,0.5)",
				strokeColor : "rgba(151,205,187,0.8)",
				highlightFill : "rgba(151,205,187,0.75)",
				highlightStroke : "rgba(151,205,187,1)",
				data : datasets[1]
			},
            {
				fillColor : "rgba(215, 185, 180,0.5)",
				strokeColor : "rgba(215, 185, 180,0.8)",
				highlightFill : "rgba(215, 185, 180,0.75)",
				highlightStroke : "rgba(215, 185, 180,1)",
				data : datasets[2]
			}
		]

	};

    var ctx = $(id).get(0).getContext("2d");
    window.myBar = new Chart(ctx).Bar(barChartData, {
        responsive : true
    });

}

