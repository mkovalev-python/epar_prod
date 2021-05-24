$(function(){
    $("input.datepicker").datetimepicker({
        'dayOfWeekStart':1,
        'format': 'd.m.Y',
	    'lang':'ru',
	    'todayButton':true,
        'closeOnDateSelect':true,
	    'timepicker': false
    });
});

$(function(){
	var dateChange = function(e){
		var now = new Date();
		var day = now.getDate();
		var month = now.getMonth() + 1;
		var year = now.getFullYear();
		if (day <= 9) day = "0" + day;
		if (month <= 9) month = "0" + month;
		var dateNow = day + '.' + month + '.' + year;

		if (e == 'day') {
			now.setDate(now.getDate() - 1);
		} else if (e == 'week') {
			now.setDate(now.getDate() - 7);
		} else if (e == 'month') {
			now.setDate(now.getMonth() - 1);
		};

		day = now.getDate();
		month = now.getMonth() + 1;
		year = now.getFullYear();
		if (day <= 9) day = "0" + day;
		if (month <= 9) month = "0" + month;
		var dateDay = day + '.' + month + '.' + year;

		$('#StartFromDate1').val(dateDay);
		$('#StartFromDate2').val(dateNow);
	};
	$('.js-date_day').on("click", function(){
		dateChange('day');
	});
	$('.js-date_week').on("click", function(){
		dateChange('week');
	});
	$('.js-date_month').on("click", function(){
		dateChange('month');
	});
});