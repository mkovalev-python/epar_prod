/**
 * Created with PyCharm.
 * User: Gvammer
 * Date: 07.05.14
 * Time: 18:38
 */
(function($){
    $(function(){
        $('.js-read-message').click(function(){
            var t = this;
            var qty;
            if ($(t).attr('rel')){
                qty = parseInt($('.js-mes_qty').text()) - 1;
            }else{
                qty = 0
            }
            $.post(
                '/messages_ajax/',
                {
                    'action': 'setRead',
                    'id': $(t).attr('rel')
                },
                function(data){
                    $('.js-mes_qty').val(qty);
                    if (qty <= 0){
                        $('.js-notificator').removeClass('fa-spin');
                    }
                }
            );
            if (qty && $(t).attr('rel'))
                $(t).closest('.js-message').remove();
            else {
                $('.js-js-pmessages-list_empty').removeClass('hidden');
                $(t).closest('.js-pmessages-dropdown').remove();
            }

            return false;
        });
    });
})(jQuery);