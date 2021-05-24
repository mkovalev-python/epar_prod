var fileList = new widgetObject({'id':'file_list'});

$.extend(fileList,{
    'currentFolder':0,
    'replaceMode':false,
    'version_of':0,
    '$selectedFile':{},
    '$fileInfoContainer':{},
    'ajax_url':'/files_ajax/',
    'lang':{
        'replaceButtonTitle':'Перенести',
        'replaceModeTitle':'Выберите папку'
    },
    'renderBreadCrumbs': function($currentfolder){
        var str = $currentfolder.text(),
            curFolder = false;
        while (curFolder = $currentfolder.closest('ul').closest('li').find('a').get(0)){
            $currentfolder = $(curFolder);
            str = '<a href="'+$currentfolder.attr('href')+'" class="js-dir-name">' + $currentfolder.text() + '</a> > ' + str;
        }
        return str;
    },
    'disableFileButtons': function (){
        $('.js-foot').hide();
    },
    'enableFileButtons': function (){
        $('.js-foot').show();
    },
    'collectSelectedFiles': function(){
        var aFilesId = [];
        this.container.find('input[name=files]:checked').each(function(){
            aFilesId.push($(this).val());
        });
        return aFilesId;
    },
    'enableReplaceMode': function(){
        var $icon = this.$replaceButton.find('i').clone();
        fileList.replaceMode = true;
        this.$replaceButton.text(fileList.lang.replaceModeTitle + ' ').append($icon);
    },
    'disableReplaceMode': function(){
        var $icon = this.$replaceButton.find('i').clone();
        fileList.replaceMode = false;
        this.$replaceButton.text(fileList.lang.replaceButtonTitle + ' ').append($icon);
    },
    'addOrRenameCategory': function(inputData){
        return this.ajaxRequest({
            'action':(inputData.$lnk.data('id')?'renameCategory':'addCategory'),
            'name':inputData.name,
            'section_id':inputData.$lnk.data('id'),
            'parent':inputData.$lnk.data('parent')
        },function(data){
            inputData.$lnk.attr('data-id',data.id);
            if (inputData.$delete_lnk)
                inputData.$delete_lnk.attr('data-dir_id',data.id);
        });
    },
    'showSelectedFileInfo': function(){
        $('.js-infoRow').hide();
        if (!this.$selectedFile) {
            return false;
        }
        var oDataSet = this.$selectedFile.data();
        for (var key in oDataSet){
            if (oDataSet[key]) {
                var oContainer = $('.js-file_' + key);
                if (oContainer.get(0)) {
                    if (oContainer.is('img')) {
                        var sImgSrc = this.$selectedFile.find('a.js-download').attr('href');
                        oContainer.attr('src', oDataSet[key]).closest('a').attr('href', sImgSrc);
                    } else if (key == 'src') {
                        oContainer.attr('href', oDataSet[key]);
                    } else {
                        oContainer.text(oDataSet[key]);
                    }
                    oContainer.closest('.js-infoRow').show();
                }
            }
        }
        if (oDataSet['versionsexist'] == 'Y'){
            var t = this;
            this.getFileVersions(oDataSet['id'], function(files){
                t.constructVersionsList(files);
            });
        }
    },
    'getFileVersions':function(fileId, callback){
        return this.ajaxRequest({
            'file_id':fileId,
            'action':'getVersionsList'
        },callback);
    },
    'constructVersionsList': function(files){
        this.$fileVersionsContainer.empty();
        if (files.length > 0){
            for (var i in files){
                var file = files[i];
                var $fileBlock = $('<li></li>');
                var $fileLink = $('<a></a>').attr('href',file.url).text(file.name);
                $fileBlock.text(' '+file.date_create).prepend($fileLink);
                this.$fileVersionsContainer.append($fileBlock)
            }
            this.$fileVersionsBlock.show();
        }
    },
    'ajaxRequest':function(data,callback){
        return PM_AjaxPost(this.ajax_url,data,callback,'json');
    },
    'getElementOfCurrentFolder': function(){
        if (this.currentFolder){
            return $('.js-dir-name[data-id='+this.currentFolder+']').closest('li');
        }
        return false;
    },
    'appendFile': function(oFile){
        this.$fileListContainer.append(oFile.getTemplateRow(this.fileTpl));
    },
    'prependFile': function(oFile){
        this.$fileListContainer.prepend(oFile.getTemplateRow(this.fileTpl));
    }
});

fileList.init = function(){
    this.$fileListContainer = $('.js-file-list');
    this.$fileInfoContainer = $('.js-fileInfo');
    this.$fileVersionsContainer = $('.js-fileVersionsList');
    this.$fileVersionsBlock = $('.js-fileVersionsBlock');
    this.$fileButtons = $('.js-fileButtonsGrp button');
    this.$replaceButton = $('.js-replaceFiles');
    this.container = $('.widget.file_list');
    this.directoryLinksSelector = 'a.js-dir-name';
    this.fileTpl = widget_file_list_file_tpl;
    this.aStartFileList = widget_file_list_arFiles;
    var t = this;

    for (var i in this.aStartFileList){
        this.appendFile(new fileObject(this.aStartFileList[i]));
    }
    $('#create_new_folder').click(function(e){
        var name = 'Новая папка',
            $lnk = $('<a class="js-dir-name" href="" ></div>').text(name).attr('contenteditable','true'),
            $list_item = $('<li></li>'),
            $delete_lnk = $('<i title="Удалить папку" class="fa fa-times-circle js-delete_dir"></i>');

        $list_item.append($lnk).append($delete_lnk);
        if (fileList.currentFolder){
            $lnk.data('parent',fileList.currentFolder);
            var $curFolderElem = fileList.getElementOfCurrentFolder();
            var $listOfFolders = $curFolderElem.find('ul');
            if (!$listOfFolders.get(0)){
                $listOfFolders = $('<ul></ul>').appendTo($curFolderElem);
            }
        }else{
            $listOfFolders = $('ul.js-dir-list')
        }
        $listOfFolders.append($list_item);

        var addCategoryLocal = function(e){
            $lnk.attr('contenteditable',false).trigger('blur');
            fileList.addOrRenameCategory({
                'name':$lnk.text(),
                '$lnk':$lnk,
                '$delete_lnk':$delete_lnk
            });
            return false;
        }

        $lnk.focus().selectText().enterPressed(function(e){addCategoryLocal(e)});
        $(document).one('click', function(e){addCategoryLocal(e)});

        e.stopPropagation();
        return false;
    });


    this.container.on('click', fileList.directoryLinksSelector, function(){
        var t = this;
        if (fileList.replaceMode){
            if (!$(t).hasClass('active')){
                if (confirm('Вы действительнто хотите перенести эти файлы в папку "' + $(t).text() + '"?')){
                    var aFilesId = fileList.collectSelectedFiles();
                    fileList.ajaxRequest({
                        'action':'replaceFiles',
                        'files':aFilesId,
                        'section_id':$(t).data('id')
                    },function(aReplacedFiles){
                        for (var i in aReplacedFiles){
                            $('input[name=files][value=' + aReplacedFiles[i] + ']')
                                .closest('li').remove();
                        }
                    });
                    fileList.disableReplaceMode();
                }
            }
        }else{
            $('ul.js-dir-list li > a').removeClass('active');
            if (!$(t).hasClass('js-root')){
                $(t).addClass('active');
            }
            $('.js-breadcrumb').html(fileList.renderBreadCrumbs($(this)));
            fileList.currentFolder = $(t).data('id');
            fileList.disableFileButtons();
            //TODO: сделать через historyManager
            document.location.hash = $(this).attr('href');
            fileList.ajaxRequest({
                'action':'getFileList',
                'section_id':fileList.currentFolder
            },function(aFiles){
                fileList.$fileListContainer.empty();
                for (var i in aFiles){
                    var obFile = new fileObject(aFiles[i]);
                    fileList.appendFile(obFile);
                }
            });
        }
        //return false;
    })
    .on('mouseup',fileList.directoryLinksSelector,function(e){
        var t = this;
        if ($(t).hasClass('active')){
            $(t).setEditable(function(){
                var t = this;
                fileList.addOrRenameCategory({
                    'name':t.text(),
                    '$lnk':t
                });
            });
        }
        e.stopPropagation();
        return false;
    });

    this.$fileListContainer.on('click', 'input[name=files]', function(e){
        $('input[name=files]').not(this).attr('checked', false).closest('.js-file').removeClass('active');
        var $label = $(this).closest('.js-file'),
            $selectedFiles = $('input[name=files]:checked');

        if ($(this).is(':checked')) {
            $label.addClass('active');
        }else{
            $label.removeClass('active');
        }
        if ($selectedFiles.size() == 1) {
            t.$selectedFile = $selectedFiles.eq(0).closest('li');
        } else {
            t.$selectedFile = false;
        }
        if ($selectedFiles.get(0)){
            fileList.enableFileButtons()
        }else{
            fileList.disableFileButtons();
        }
        t.showSelectedFileInfo();
        e.stopPropagation();
    });

    $('.js-dir-list').on('click', '.js-delete_dir', function(e){
        if (confirm("Вы действительно хотите удалить эту папку?")){
            var oCurLink = this;
            fileList.ajaxRequest({
                'action':'deleteDir',
                'dirId':$(oCurLink).data('dir_id')
            },function(oResult){
                if (oResult.success == 'Y'){
                    $(oCurLink).closest('li').remove();
                }
                $('span.root a').trigger('click'); //перейдем в корень проекта
            });
            e.stopPropagation();
            return false;
        }
    });

    var $delButton = $('.js-deleteFiles');
    $delButton.click(function(){
        if (confirm("Вы действительно хотите удалить эти файлы?")){
            var aFilesId = fileList.collectSelectedFiles();
            fileList.ajaxRequest({
                'action':'deleteFiles',
                'files':aFilesId
            },function(aDeletedFiles){
                for (var i in aDeletedFiles){
                    $('input[name=files][value=' + aDeletedFiles[i] + ']')
                        .closest('li').remove();
                }
            });
        }
    });

    this.$replaceButton.click(function(){
        if (fileList.replaceMode){
            fileList.disableReplaceMode();
        }else{
            fileList.enableReplaceMode();
        }
    });

    this.container.on('click', '.jsAddNewVersion', function(e){
        t.version_of = $(this).data('file_id');
        t.container.find('input:file').bind('click.silent',function(e){e.stopPropagation();}).trigger('click').unbind('click.silent');

        e.stopPropagation();
        return false;
    });

    $(document).click(function(){
        fileList.version_of = 0;
    });

    this.initFileUpload();

    $('.tmp_script').remove();

    if (document.location.hash) {
        $('[href='+document.location.hash+']').trigger('click');
    }
}

fileList.initFileUpload = function(){
    var errorHandler = function(){
        alert('Не удалось загрузить файл');
    };

    $('.filelist-file-upload').fineUploader({
        debug: false,
        button: $('.file_upload_button').get(0),
        request: {
            endpoint: "/upload/receiver",
            paramsInBody: true,
            customHeaders: {
                "X-CSRFToken": $.cookie('csrftoken')
            }
        },
        text: {
            cancelButton:'Отмена',
            retryButton:'Повторить',
            deleteButton:'Удалить'
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
            //params: {foo: "bar"}
        },
        display: {
            completeFileDelete: true,
            fileSizeOnSubmit: true
        }
        ,
        paste: {
            targetElement: $(document)
        }
    })
        .on('error', errorHandler)
        .on('uploadChunk resume', function(event, id, fileName, chunkData) {
            qq.log('on' + event.type + ' -  ID: ' + id + ", FILENAME: " + fileName + ", PARTINDEX: " + chunkData.partIndex + ", STARTBYTE: " + chunkData.startByte + ", ENDBYTE: " + chunkData.endByte + ", PARTCOUNT: " + chunkData.totalParts);
        })
        .on("upload", function(event, id, filename) {
            $(this).fineUploader('setParams', {"section_id": fileList.currentFolder, "version_of": fileList.version_of}, id);
        })
        .on("complete",function(event,id,filename,data){
            if (data.id){
                $(this).fineUploader('setDeleteFileParams', {"file_id": data.id}, id);
                var oFile = new fileObject(data);
                fileList.prependFile(oFile);
            }
        });
}

fileList.search = function (text) {
        fileList.ajaxRequest({
                'action':'getFileList',
                'section_id':fileList.currentFolder,
                'search': text
            },function(aFiles){
                fileList.$fileListContainer.empty();
                for (var i in aFiles){
                    var obFile = new fileObject(aFiles[i]);
                    fileList.appendFile(obFile);
                }
            });
    };

$(function(){
    fileList.init();
});

var fileObject = function(data){
    if (!data) data = {};
    for (var i in data){
        if (!this[i]){
            this[i] = data[i];
        }
    }

    return this;
}

fileObject.prototype = {
    getTemplateRow:function(tpl){
        var t = this;
        var iconClass = getIconForExtension(t.type);
        var thumb = '';
        if (t.isPicture)
            thumb = '<span style="background:url(' + t.thumbnail + ');"></span>';
        else if (iconClass)
            thumb = '<i class="fa fa-file-'+iconClass+'-o"></i>';
        else
            thumb = '<i class="fa fa-file-o"></i>';

        t['thumb'] = thumb;
        for (var i in t){
            if (t.hasOwnProperty(i) && !(t[i] instanceof Function)){
                var strRegExp = '#'+i+'#';
                tpl = tpl.replace(new RegExp(strRegExp,'mig'),t[i]);
            }
        }

        this.$content = $(tpl);
        if (t.hasOldVersions) {
            this.$content.find('.js-showVersions').show();
        } else {
            this.$content.find('.js-showVersions').hide();
        }

        for (var key in t){
            if (!(t[key] instanceof Function) && !((t[key] instanceof Object))){
                this.$content.attr('data-'+key, t[key]);
            }
        }
        return this.$content;
    }
}