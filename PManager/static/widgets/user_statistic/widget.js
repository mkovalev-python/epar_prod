$(function(){
    $("input.datepicker").datetimepicker({
        'dayOfWeekStart': 1,
        'format': 'd.m.Y',
        'lang':'ru',
        'todayButton':true,
        'closeOnDateSelect': true,
        'timepicker': false
    });
});
