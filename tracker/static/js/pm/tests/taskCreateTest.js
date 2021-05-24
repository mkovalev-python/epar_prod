/**
 * Created with PyCharm.
 * User: Gvammer
 * Date: 29.06.14
 * Time: 22:00
 */
(function($){
    $(function(){
        var title = 'Новая тестовая задача'+(new Date());
        $('input.task-create').val(title);
        $('button.task-create').trigger('click');
        setTimeout(function(){
            test( "Message model init", function() {
                var tl = $('.js-name-link:eq(0)');
                console.log(title);
              ok($.trim(tl.text()) == title, 'Успешно добавлено');
                var play = tl.closest('.task').find('.fa-play-circle').trigger('click');
                setTimeout(function(){
                    play.trigger('click');
                    tl.closest('.task').find('.pause_comment_cancel').trigger('click');
                }, 2000);

            })
        }, 3000);
    })
})(jQuery);