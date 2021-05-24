/**
 * Created by tracker_maker on 28.02.15.
 */
(function($){
    window.ajaxInputs = function(params){
        if (!params) params = {};
        var selector = '.js-ajax-input';
        var postData = function(elem) {
            var val = $(elem).val();
            if ($(elem).is('[type=checkbox]')) val = $(elem).is(':checked') * 1;
            return $.post(
                document.URL,
                $.extend($(elem).data(), {'value': val}),
                params.callback || false
            );
        };

        var r = function(e){
            var t = this;
            if ($(this).is(':text')) {
                var to = $(this).data('ajaxTimeout');
                if (to) clearTimeout(to);

                to = setTimeout(function(){
                    $(t).data('ajaxTimeout', false);
                    postData(t);
                }, 500);

                $(t).data('ajaxTimeout', to)
            } else {
                postData(t);
            }
        };

        $(document).on('keyup change', selector, r).on('click', 'button'+selector+', '+selector+':submit', r);
    };
})(jQuery);