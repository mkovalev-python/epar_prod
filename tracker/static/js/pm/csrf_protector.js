;(function(){
	var csrfSafeMethod = function csrfSafeMethod(method){
			return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
		},
		sameOrigin = function sameOrigin(url){
			var host = document.location.host,
				protocol = document.location.protocol,
				sr_origin = '//' + host,
				origin = protocol + sr_origin;
			return (url === origin || url.slice(0, origin.length + 1) === origin + '/') ||
				(url === sr_origin || url.slice(0, sr_origin.length + 1)  === sr_origin + '/') ||
				!(/^(\/\/|http:|https:).*/.test(url));
		};
	$.ajaxSetup({
		beforeSend: function(xhr, settings) {
			if(!csrfSafeMethod(settings.type) && sameOrigin(settings.url)){
				xhr.setRequestHeader('X-CSRFToken', heliardSettings.CSRF_TOKEN);
			}
		}
	});
})();