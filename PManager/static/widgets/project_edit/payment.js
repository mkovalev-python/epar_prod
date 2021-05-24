;$(function(){
    var JS_BONUS_COMPLETE = '.js-bonus-complete',
        JS_USER_PAY_WIN = '.js-user-pay-win',
        JS_REMOVE_ROLE = '.js-remove-role',
        JS_INPUT_USER_SUM = '.js-input-user-sum',
        JS_INPUT_ROLE_ID = '.js-input-role-id',
        JS_SEND_PAYMENT_BUTTON = '.js-send-payment-button',
        JS_INPUT_COMMENT = '.js-input-comment',
        JS_SEND_PAYMENT_FORM = '.js-send-payment-form',
        URL = document.URL,
        sendPayment = function(el) {
            var $form = $(el).closest(JS_SEND_PAYMENT_FORM),
                data = {
                    action: 'send_payment',
                    role: parseInt($form.find(JS_INPUT_ROLE_ID).val()),
                    sum: parseInt($form.find(JS_INPUT_USER_SUM).val()),
                    comment: $form.find(JS_INPUT_COMMENT).val()
                };
            PM_AjaxPost(
                URL,
                data,
                function (data) {
                    if (data['result']) document.location.reload();
                },
                'json'
            );
        };

    $(JS_BONUS_COMPLETE).click(function() {
        $.fancybox({
            'content': $(JS_USER_PAY_WIN).html()
        });
        $(JS_INPUT_USER_SUM).val($(this).data('sum') * -1);
        $(JS_INPUT_ROLE_ID).val($(this).attr('rel'));
        return false;
    });

    $(JS_REMOVE_ROLE).click(function() {
        var t = this;
        PM_AjaxPost(
                URL,
                {
                    'action': 'remove_role',
                    'role': $(this).data('role')
                },
                function (data) {
                    if (data.error) {
                        alert(data.error);
                    } else {
                        $(t).closest('.js-role-block').remove();
                    }
                },
                'json'
            );
        return false;
    });

    $(document).on('click', JS_SEND_PAYMENT_BUTTON, function(){
        sendPayment(this);
        return false;
    });
});