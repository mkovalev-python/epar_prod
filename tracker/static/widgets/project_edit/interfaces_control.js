;$(function(){
    var JS_PROJECT_SUBMIT = '.js-project-submit',
        JS_ADD_INTERFACE = '.js-add-interface-form',
        JS_INTERFACE_CONTAINER = '.js-interface-container',
        JS_COPY_PASSWORD = '.js-copy-password',
        JS_ADD_INTERFACE_WRAPPER = '.js-add-interface-wrapper',
        JS_ADD_INTERFACE_INPUT = '.js-add-interface-input',
        JS_INTERFACE_REMOVE = '.js-interface-remove',
        JS_INTERFACE_BLOCK = '.js-interface-block',
        JS_INTERFACE_FORM_CLOSE = '.js-interface-modal-close';

    $(JS_PROJECT_SUBMIT).click(function(){
        $(JS_ADD_INTERFACE).ajaxSubmit(function(data){
            var $ic = $(JS_INTERFACE_CONTAINER);
            $ic.append(data);
            $(JS_ADD_INTERFACE_WRAPPER)
                .find(JS_ADD_INTERFACE_INPUT)
                .val('')
            .end()
                .find(JS_INTERFACE_FORM_CLOSE).click();

            if (clipboardAppend)
                clipboardAppend($ic.find(JS_COPY_PASSWORD).last());

        });
        return false;
    });

    $(JS_INTERFACE_CONTAINER).on('click', JS_INTERFACE_REMOVE, function () {
        var $interface = $(this).closest(JS_INTERFACE_BLOCK),
            id = $interface.data('id');
        $interface.remove();
        PM_AjaxPost(
                '/remove_interface/',
                {
                    'id': id
                }
        );
    });
});
