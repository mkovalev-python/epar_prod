;(function($){
    var INVITE_BUTTON_TRIGGER_SELECTOR = '.js-taskdraft-invite-user',
        taskdraft = window.heliardData.draft,
        url = '/taskdraft/' + taskdraft.slug + '/accept-developer'
    $(INVITE_BUTTON_TRIGGER_SELECTOR).click(function(ev){
        ev.stopPropagation();
        ev.preventDefault();
        var self = this,
            data = { user_id: $(this).data('userid') };
        $.post(url, data, function(response){
            alert(response.result);
            if(response.hasOwnProperty('result') && response.result != ""){
                $(self).unbind('click');
                $(self).hide();
                $(self).remove();
            }
        });

    });
})(jQuery);
