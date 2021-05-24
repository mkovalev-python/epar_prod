;$(function(){
    //var timerCheckFields = false,
    //    JS_PROJECT_NAME_INPUT = '.js-project-name',
    //    JS_REPOSITORY = '.js-repository',
    //    JS_REPOSITORY_VALUE = '.js-repository-value',
    //    JS_HIDDABLE = '.js-hiddable',
    //    JS_SUBMIT_FORM_BUTTON = '.js-integration-save',
    //    AJAX_POST_URL = '/project/edit/check_repository_name',
    //    timerCheckFields = false,
    //    currentRepositoryName = '',
    //    $projectNameInput = $(JS_PROJECT_NAME_INPUT),
    //    $projectRepository = $(JS_REPOSITORY),
    //    $repositoryField = $(JS_REPOSITORY_VALUE),
    //    $popInElement = $(JS_HIDDABLE),
    //    submit = {
    //        $el: $(JS_SUBMIT_FORM_BUTTON),
    //        enable: function(){
    //            this.$el.removeAttr('disabled');
    //        },
    //        disable: function(){
    //            this.$el.attr('disabled', 'disabled');
    //        }
    //    },
    //    checkFields = function() {
    //        var $spinner = $repositoryField.next('i'),
    //            repoName = $repositoryField.val();
    //        if(repoName === currentRepositoryName){
    //            return;
    //        }
    //        $spinner.addClass('fa-spinner fa-spin');
    //        PM_AjaxPost(
    //            AJAX_POST_URL,
    //            {
    //                'repoName': repoName
    //            },
    //            function (response) {
    //                if (response == "OK") {
    //                    $spinner.attr('class', 'fa fa-icon fa-check-circle').css('color', 'green');
    //                    currentRepositoryName = repoName;
    //                    submit.enable();
    //                } else if (response == "ERROR") {
    //                    $spinner.attr('class', 'fa fa-icon fa-exclamation-circle').css('color', 'red');
    //                    submit.disable();
    //                } else {
    //                    $repositoryField.val(response);
    //                    currentRepositoryName = response;
    //                    $spinner.attr('class', 'fa fa-icon fa-check-circle').css('color', 'green');
    //                    submit.enable();
    //                }
    //            }
    //        );
    //    },
    //    timerHalt = function(fn, resetFunc){
    //        if(timerCheckFields){
    //            clearTimeout(timerCheckFields);
    //        }
    //        if(resetFunc !== false){
    //            timerCheckFields = setTimeout(fn, 700)
    //        }
    //    };
    //
    //    if($projectRepository.is(':disabled')){
    //        return false;
    //    }
    //    $projectRepository.change(function(){
    //        if($projectRepository.is(':checked')){
    //            $repositoryField.val(transliterate($projectNameInput.val()));
    //            $popInElement.show();
    //            checkFields();
    //            submit.disable();
    //        }else{
    //            $repositoryField.val('');
    //            $popInElement.hide();
    //            submit.enable();
    //        }
    //    });
    //
    //    $repositoryField.focus(function() {
    //        checkFields();
    //    }).keyup(function() {
    //        timerHalt(checkFields);
    //    }).blur(function(ev) {
    //        timerHalt(checkFields, false);
    //    });
});