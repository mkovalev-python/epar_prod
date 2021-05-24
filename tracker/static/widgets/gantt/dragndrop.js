/**
 * Created with PyCharm.
 * User: Gvammer
 * Date: 15.07.14
 * Time: 23:32
 */
$.fn.setEventPosition = function(x, y) {
    return this.css({
            'left': x-5,
            'top': y-5
        })
};

function bindDragNDrop(callback) {
    var $movedTask = false;
    var highlightRowClass = 'highlighted';
    $(document).on('mousedown.taskdnd','.js-drag-task:not(.closed *)',function(e){
        $movedTask = $(this).closest('.gantt-event');
        if (!$movedTask.data('parent'))
            $movedTask.data({
                'left': $movedTask.css('left'),
                'top': $movedTask.css('top'),
                'parent': $movedTask.parent().get(0)
            }).appendTo('body');
        var x = e.clientX, y= e.clientY + $(window).scrollTop();
        $movedTask.setEventPosition(x, y);
    });

    $(document).bind('mouseup.taskdnd',function(){
        if ($movedTask && $movedTask.get(0)) {
            var assigned;

            var $highLightedResp = $('.gantt-event-desk td > div.'+highlightRowClass);
            $movedTask.css({
                'top': $movedTask.data('top')
            });

            if ($highLightedResp.get(0)){
                var respId = $highLightedResp.data('responsible');
                var $lastEventInRow = $highLightedResp.find('.gantt-event:last');
                if (callback($movedTask.data('id'), respId)) {
                    assigned = true;
                }
                $('.gantt-event-desk td > div').removeClass(highlightRowClass);
            }

            if (!assigned) {
                //push task back
                $movedTask.css({
                    'left': $movedTask.data('left')
                });
                $movedTask.appendTo($movedTask.data('parent'));
            }
            $movedTask.data('parent', false);
            $movedTask = false;
        }
    }).on('mousemove.taskdnd' , function (e){
        if ($movedTask && $movedTask.get(0)) {
            var x = e.clientX, y = e.clientY + $(window).scrollTop();
            $movedTask.setEventPosition(x, y);

            //highlight responsibles
            $('.gantt-event-desk td > div').each(function(){
                var trY = $(this).offset().top;
                var trHeight = $(this).height();
                if (y > trY && y < (trY + trHeight)) {
                    $(this).addClass(highlightRowClass);
                } else {
                    $(this).removeClass(highlightRowClass);
                }
            });
        }
    });
}