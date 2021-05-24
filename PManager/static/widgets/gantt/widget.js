$(function () {
    var gantt = new GANTT(
        {
            'container': $('.gantt-overflow')
        },
        GANTT_TASKS,
        MILESTONES
    );
    bindDragNDrop(function(id, respId){ return gantt.assignEventTo(id, respId); });

    $(window).scroll(function(){
        var $el = $('.js-top-thumb-container');
        if ($('html, body').scrollTop() > 150) {
            $el.addClass('gant-scrollable')
        } else {
            $el.removeClass('gant-scrollable')
        }
    })
});