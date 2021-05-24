;(function($){
  $(document).ready(function(){
     $('.js-tasks').on('click', '.js-accept-developer', function(ev){
         ev.preventDefault();
         var data = $(this).parent('form').serializeArray(),
             user_id = data[0].value,
             url = $(this).parent('form').attr('action'),
             self = this;
         $.post(url, data, function(response){
            if(response.error){
                toastr.error(response.error);
            }else if(response.result) {
                toastr.info(response.result);
                $(self).parents('.task-wrapper').fadeOut(function(){
                  $(document).find('.js-taskdraft-invite-user[data-userid=' + user_id + ']').fadeOut();
                  $(this).remove();
                })
            }
         });
         return false;
     });
     $('.js-tasks').on('click', '.js-send-task-submit', function(ev){
          ev.preventDefault();
          ev.stopPropagation();
          var self = this,
              form = $(this).parents('.js-send-task-form'),
              messages_container = form.parents('.js-task-discussion').find('.js-discussion-messages'),
              url = form.attr('action'),
              data = form.serializeArray();

          $.post(url, data, function(response){
              $(messages_container).append(response);
              form[0].reset();
          });


          return false;
     });
  });
})(jQuery);
