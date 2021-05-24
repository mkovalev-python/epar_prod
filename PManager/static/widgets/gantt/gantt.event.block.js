/**
 * Created with PyCharm.
 * User: Gvammer
 * Date: 27.07.14
 * Time: 17:23
 */
var EventBlock = function (event) {
    var $eventBlock = $('.gantt-event[data-id='+event.id+']');
    if ($eventBlock.get(0)) {
        this.$elem = $eventBlock;
    } else {
        this.$elem = $('<div></div>', {
                'class': 'gantt-event'
            }
        );
        if (event.title)
            this.$elem.append('<i class="fa fa-ellipsis-v js-drag-task" style="height: 22px;"></i>')
            .append('<a href="' + event.url + '">' + event.title + '</a>');
    }

    this.$elem.attr('data-id', event.id);
    if (event.title) {
        if (event.planTime)
            this.$elem.append(
                    '<div class="gantt-event-plantime">Оценка: <span>' + event.planTime + ' ч.</span></div>'
            );
    }
    if (event.isMyProject && event.isMilestoneStarted) {
        this.$elem.addClass('my_started');
    }
    if (!event.isMyProject && event.isMilestoneStarted) {
        this.$elem.addClass('not_my_started');
    }
    if (event.isMyProject && !event.isMilestoneStarted) {
        this.$elem.addClass('my_not_started');
    }
    if (!event.isMyProject && !event.isMilestoneStarted) {
        this.$elem.addClass('not_my_not_started');
    }
};
EventBlock.prototype = {

};