$(document).ready(function(){
    var $form = $('.js-form-key');
    $form.submit(function(e){ e.preventDefault();})
    $('.js-submitKey').click(function(e){
        e.preventDefault();
        var $submit = $(this),
            url = $form.attr('action'),
            data = $form.serializeArray();
        $submit.prop('disabled', true);
        $.post(url, data, function(response){
            if(response.result === 'errors') {
                var fillErrors = function(elName, text){
                        $('[name="key_' + elName + '"]').parents('.form-group').addClass('has-error');
                        var tooltip = $('#key_' + elName + '_tooltip');
                        tooltip.attr('data-original-title', text)
                        .tooltip('fixTitle');
                        tooltip.click(function(e){
                            e.preventDefault();
                            return false;
                        });
                        tooltip.attr('rel', 'tooltip');
                        tooltip.show();
                    },
                    clearErrors = function(elName){
                        var tooltip = $('#key_' + elName + '_tooltip');
                        $('[name="key_' + elName + '"]').parents('.form-group').removeClass('has-error');
                        tooltip.hide();
                    };
                if(response.fields['name']){
                    fillErrors('name', response.fields['name'])
                }else{
                    clearErrors('name');
                }
                if(response.fields['data']){
                    fillErrors('data', response.fields['data'])
                }else{
                    clearErrors('data');
                }

                $("[rel='tooltip']").tooltip();
                $submit.prop('disabled', false);
                return false;
            }
            else{
                location.reload();
            }
            return false;
        });
        return false;
    });
    $('.popup').find('.form-control').focus(function(){
        $('.popup').find('.form-group').removeClass('has-error');
        $("[rel='tooltip']").hide();
    });
});