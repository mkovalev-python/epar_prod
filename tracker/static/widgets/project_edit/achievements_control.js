;$(function(){
    var JS_SELECT_ACHIEVEMENT = '.js-select-achievement',
        JS_ACHIEVEMENT = '.js-achievement',
        JS_ACHIEVEMENT_INPUTS = 'select, input:not(:checkbox)',
        JS_INPUTS_FILTER = 'input:text';

    $(JS_SELECT_ACHIEVEMENT).click(function() {
        var $inp, 
            checked = $(this).is(':checked'),
            func = (checked ? 'addClass': 'removeClass'),
            $inputs = $(this).closest(JS_ACHIEVEMENT)[func]('active')
                .find(JS_ACHIEVEMENT_INPUTS)
                .attr('disabled', (checked ? false: 'disabled'));

        if (checked) {
            $(this).attr('checked', 'checked');
            $inp = $inputs.filter(JS_INPUTS_FILTER);
            if ($inp.val()) $inp.trigger('change');
        }
    });
});
