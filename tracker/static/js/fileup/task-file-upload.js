function taskFileUpload(complete1, errorHandler, completeDelete) {
    if (!errorHandler)
        errorHandler = function () {
            alert('Не удалось загрузить файл');
        };



    return $('.task-file-upload').each(function () {
        var t = this;
        var complete = function (event, id, filename, data) {
            if (data.id) {
                $('<input type="hidden" name="files'+($(t).data('postfix') || '')+'" />').val(data.id).appendTo($(t));
                $(this).fineUploader('setDeleteFileParams', {"file_id": data.id}, id);
            }
            complete1 && complete1(event, id, filename, data);
        };

        $(this).fineUploader({
            debug: false,
            button: $(this).closest('.file-adding-form').find('.file_upload_button').get(0),
            request: {
                endpoint: "/upload/receiver",
                paramsInBody: true,
                customHeaders: {
                    "X-CSRFToken": $.cookie('csrftoken')
                }
            },
            text: {
                cancelButton: 'Отмена',
                retryButton: 'Повторить',
                deleteButton: 'Удалить'
            },
            chunking: {
                enabled: true
            },
            resume: {
                enabled: true
            },
            retry: {
                enableAuto: true,
                showButton: true
            },
            deleteFile: {
                enabled: true,
                endpoint: '/upload/receiver',
                forceConfirm: false,
                customHeaders: {
                    "X-CSRFToken": $.cookie('csrftoken')
                }
            },
            display: {
                completeFileDelete: completeDelete,
                fileSizeOnSubmit: true
            }
        })
            .on('error', errorHandler)
            .on('uploadChunk resume', function (event, id, fileName, chunkData) {
                qq.log('on' + event.type + ' -  ID: ' + id + ", FILENAME: " + fileName + ", PARTINDEX: " + chunkData.partIndex + ", STARTBYTE: " + chunkData.startByte + ", ENDBYTE: " + chunkData.endByte + ", PARTCOUNT: " + chunkData.totalParts);
            })
            .on("upload", function (event, id, fileame) {
                $(this).fineUploader('setParams', {"project": window.currentProject}, id);
            })
            .on("complete", complete);
    });

}

var $attachedFileBlock = function (path, name, id, type, thumb) {
    var fileBlock;
    if (type == 'docx' || type == 'doc') {
        fileBlock = '<i class="fa fa-file-word-o"></i>'
    } else if (type == 'xlsx' || type == 'xls') {
        fileBlock = '<i class="fa fa-file-excel-o"></i>'
    } else if (type == 'zip' || type == 'rar' || type == 'gz') {
        fileBlock = '<i class="fa fa-file-archive-o"></i>'
    } else if (type == 'pptx' || type == 'ppt') {
        fileBlock = '<i class="fa fa-file-powerpoint-o"></i>'
    } else if (thumb) {
        fileBlock = '<img src="' + thumb + '">'
    } else {
        fileBlock = '<i class="fa fa-file-o"></i>'
    }

    return $('<a class="uploaded_file-item js-file-item" href="" data-toggle="tooltip" data-placement="top" title="' + name + '">' +
        '<span class="uploaded_file-item-image">' + fileBlock + '</span>' +
        '<span class="fa fa-remove" onclick="$(this).closest(\'.js-file-item\').remove();"></span>' +
        '<input name="files" value="' + id + '" type="hidden" />' +
        '</a>').tooltip();
};