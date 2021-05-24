;$(function(){
    //todo: refactor this repetition of code
    var JS_EDITABLE_TEXTAREA_CLICK = '.editable-textarea-click',
        JS_EDITABLE_TEXTAREA = '.editable-textarea',
        JS_EDITABLE_EDIT_LINK = '.project-edit-link-editable',
        JS_EDITABLE_EDIT_INPUT = '.project-edit-input',
        JS_PROJECT_CONTROLS = '.editable-textarea, .project-edit-input',
        JS_PROJECT_CONTROL_INPUTS = '.editable-textarea-click, .project-edit-link-editable',
        JS_PROJECT_NAME = '.js-project-name',
        JS_PROJECT_DESCRIPTION = '.js-project-description',
        updateName = function() {
            PM_AjaxPost(
                    document.URL,
                    {
                        'action': 'change_name',
                        'name': $(JS_PROJECT_NAME).val(),
                        'description': $(JS_PROJECT_DESCRIPTION).val()
                    },
                    function (data) {

                    },
                    'json'
            );
        };
    
    window.ajaxInputs();

    $(JS_EDITABLE_TEXTAREA_CLICK).click(function(e) {
        $(this).hide();
        $(JS_EDITABLE_TEXTAREA).show().focus().select();
        e.stopPropagation();
    });
    $(JS_EDITABLE_EDIT_LINK).click(function(e) {
        $(this).hide();
        $(JS_EDITABLE_EDIT_INPUT).show().focus().select();
        e.stopPropagation();
    });

    $(JS_PROJECT_CONTROLS).click(function(e) {
        e.stopPropagation();
    });

    $(JS_EDITABLE_TEXTAREA).keyup(function(){
        $(JS_EDITABLE_TEXTAREA_CLICK).text($(this).val())
    });

    $(JS_EDITABLE_EDIT_INPUT).keyup(function(){
        $(JS_EDITABLE_EDIT_LINK).text($(this).val())
    });

    $(document).click(function () {
        var $projectControls = $(JS_PROJECT_CONTROLS);

        if ($projectControls.is(':visible')) {
            $(JS_PROJECT_CONTROL_INPUTS).show();
            $projectControls.hide();
            updateName();
        }
    });
});
