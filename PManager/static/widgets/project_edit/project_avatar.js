;$(function(){
    var JS_AVATAR_UPLOAD = '.js-avatar_upload',
        JS_AVATAR = '.js-avatar',
        PATTERN_FILE_TYPE = 'image. *',
        CURRENT_PROJECT = window.currentProject,
        URL = document.URL,
        ERROR = 'something failed',
        fileRead = function(file){
            var reader;
            if(!FileReader) { return ;}
            reader = new FileReader();
            reader.onload = function(){
                $(JS_AVATAR).attr('src', reader.result);
            };
            reader.readAsDataURL(file);
        },
        createFormData = function(file){
            var formData = new FormData();
            formData.append('image', file);
            formData.append('action', 'upload_project_avatar');
            formData.append('project', CURRENT_PROJECT);
            return formData;
        }, 
        requestAvatar = function(formData){
            req = $.ajax({
                url: URL,
                type: "POST",
                data: formData,
                processData: false,
                contentType: false
            });
            req.fail(function(){
                console.log(ERROR);
            });
            req.done(function(data){
                data = JSON.parse(data);
                $(JS_AVATAR).attr('src', data.path);
            });
        };

    $(JS_AVATAR_UPLOAD).change(function () {
        var file = this.files[0];
        if (!file.type.match(PATTERN_FILE_TYPE)) { return; }

        fileRead(file);
        requestAvatar(createFormData(file));
    });
});