(function ($) {
    $(function () {
        $(document).on('click', '.js-pay', function () {
            $('form[name=robo] .temp-summ').val(
                $(this).closest('div').find('.temp-summ').val()
            );
            document.forms.robo.submit();
            $.fancybox.close();
            return false;
        });

        $('[data-toggle="popover"]').popover({
            trigger: 'hover'
        });

        $('.js-select-role').click(function () {
            if (!$(this).is('.active')) {
                $(this).addClass('active').siblings('.js-select-role').removeClass('active');
                $('.js-role').filter('[data-role=' + $(this).data('role') + ']').show().siblings('.js-role').hide();
            }
            $('.js-graph-' + $(this).data('role')).show().siblings().hide();
        });

        $('.js-change-role').click(function () {
            var $next = $('.js-select-role.active').next('.js-select-role');
            var $first = $('.js-select-role').not('.active').eq(0);
            if ($next.get(0)) {
                $next.trigger('click');
            } else {
                $first.trigger('click')
            }
            return false;
        });

        $('.js-graph-' + $('.js-select-role.active').data('role')).show().siblings().hide();

        $(window).on('task_closed', function (taskInfo) {
            var $tClosed = $('.js-project-graph-tasks-closed'),
                $tAll = $('.js-project-graph-tasks-all'),
                $progress = $('.js-closed-tasks-progress');

            $tClosed.text(parseInt($tClosed.text()) + 1);
            $progress.css('width', Math.round(parseInt($tClosed.text()) * 100 / parseInt($tAll.text())) + '%');
        });

        $('.js-view-comments').click(function () {
            var $currentCheckBox = $('.js-comments-filter-input[value="' + $(this).data('type') + '"]');
            $('.js-widgets-tab[data-widget=chat]').not('.active').trigger('click');
            $('.js-comments-filter-input').attr('checked', false);
            setTimeout(function() {$currentCheckBox.attr('checked', 'checked').trigger('click');}, 100);

            return true;
        });
    });
})(jQuery);