/**
 * Created with PyCharm.
 * User: Gvammer
 * Date: 07.05.14
 * Time: 18:24
 */
var userDynamics = {
    'getOpenTask': function () {
        if (taskManager) {
            taskManager.taskAjaxRequest({
                'action': 'getUserLastOpenTask'
            }, function (task) {
                if (task && task['name']) {
                    toastr.info(
                        "<a href='" + task['url'] + "'>" + task['project__name'] + '/ '
                        + task['name'] + "</a>",
                        'Вы можете вернуться к задаче'
                    );
                }
            }, 'json');
        }
    }
}