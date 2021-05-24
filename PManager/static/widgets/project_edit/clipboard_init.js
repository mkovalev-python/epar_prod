;$(function () {
	var SWF_PATH = '/static/js/libs/clipboard/jquery.clipboard.swf',
		TEXT_COMPLETE = 'пароль скопирован',
		JS_COPY_PASSWORD = '.js-copy-password'; 
	clipboardAppend = function(t) {
	    $(t).clipboard({
	        path: SWF_PATH,
	        copy: function () {
	            $(t).data('text', $(t).text()).text(TEXT_COMPLETE);
	            setTimeout(function () {
	                $(t).text($(t).data('text'));
	            }, 2000);
	            return $(t).data('password');
	        }
	    });
	};
	$(JS_COPY_PASSWORD).each(function () {
	    clipboardAppend(this);
	});
});
var clipboardAppend;