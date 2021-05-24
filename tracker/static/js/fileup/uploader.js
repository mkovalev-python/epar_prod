/**
 * Class that creates upload widget with drag-and-drop and file list
 * @inherits qq.FineUploaderBasic
 */
qq.FineUploader = function(o){
    // call parent constructor
    qq.FineUploaderBasic.apply(this, arguments);

    // additional options
    qq.extend(this._options, {
        element: null,
        listElement: null,
        dragAndDrop: {
            extraDropzones: [],
            hideDropzones: true,
            disableDefaultDropzone: false
        },
        text: {
            uploadButton: 'Загрузить файл',
            cancelButton: 'Cancel',
            retryButton: 'Retry',
            deleteButton: 'Delete',
            failUpload: 'Загрузка не удалась',
            dragZone: 'Перетащите сюда файлы, чтобы загрузить',
            dropProcessing: 'Загружаю файлы...',
            formatProgress: "{percent}% of {total_size}",
            waitingForResponse: "Подождите...",
            doubletext: "прикреплен к другой задаче"
        },
        template: (!this._options.button ? '<div class="qq-upload-button"></div>' : '') +
            '<div class="qq-uploader" >' +
            ((!this._options.dragAndDrop || !this._options.dragAndDrop.disableDefaultDropzone) ? '<div class="qq-upload-drop-area mini-layout"><span>{dragZoneText}</span></div>' : '') +
            '<span class="qq-drop-processing"><span">{dropProcessingText}</span><span class="qq-drop-processing-spinner"></span></span>' +
            (!this._options.listElement ? '<ul class="qq-upload-list"></ul>' : '') +
            '</div>',

        // template for one item in file list
        fileTemplate: '<li>' +
                            '<div class="qq-progress-bar"></div>' +
                            '<span class="qq-upload-spinner"></span>' +
                            '<span class="qq-upload-finished"></span>' +
                            '<span class="qq-upload-file"></span>' +
                            '<span class="qq-upload-size"></span>' +
                            '<div class="btn-group">' +
                            '<a class="qq-upload-cancel btn btn-warning btn-mini" href="#"><i class="fa fa-stop icon-white"></i></a>' +
                            '<a class="qq-upload-retry btn btn-mini" href="#"><i class="fa fa-refresh "></i></a>' +
                            '<a class="qq-upload-delete btn btn-danger btn-mini" href="#"><i class="fa fa-trash-o icon-white"></i></a>' +
                            '<a class="qq-up-reup btn btn-primary btn-mini" style="display: none; color: white" href="#">Добавить</a>' +
                            '<a class="qq-up btn btn-secondary btn-mini" href="#" style="display: none; color: #3333d7" >Прикрепить</a>' +
                            '<a class="qq-cancel btn btn-secondary btn-mini" href="#" style="display: none; color: #3333d7"></i>Отменить</a>' +
                            '</div>' +
                            '<span class="qq-upload-status-text">{statusText}</span>' +
                        '</li>',
        classes: {
            button: 'qq-upload-button',
            drop: 'qq-upload-drop-area',
            dropActive: 'qq-upload-drop-area-active',
            dropDisabled: 'qq-upload-drop-area-disabled',
            list: 'qq-upload-list',
            progressBar: 'qq-progress-bar',
            file: 'qq-upload-file',
            spinner: 'qq-upload-spinner',
            finished: 'qq-upload-finished',
            retrying: 'qq-upload-retrying',
            retryable: 'qq-upload-retryable',
            size: 'qq-upload-size',
            cancel: 'qq-upload-cancel',
            deleteButton: 'qq-upload-delete',
            retry: 'qq-upload-retry',
            statusText: 'qq-upload-status-text',

            success: 'qq-upload-success',
            fail: 'qq-upload-fail',

            successIcon: null,
            failIcon: null,

            dropProcessing: 'qq-drop-processing',
            dropProcessingSpinner: 'qq-drop-processing-spinner',

            upAndReload: 'qq-up-reup',
            upNew: 'qq-up',
            cancelNew: 'qq-cancel',

        },
        failedUploadTextDisplay: {
            mode: 'default', //default, custom, or none
            maxChars: 50,
            responseProperty: 'error',
            enableTooltip: true
        },
        messages: {
            tooManyFilesError: "You may only drop one file"
        },
        retry: {
            showAutoRetryNote: true,
            autoRetryNote: "Загружаю {retryNum}/{maxAuto}...",
            showButton: false
        },
        deleteFile: {
            forceConfirm: true,
            confirmMessage: "Вы уверены, что хотите удалить {filename}?",
            deletingStatusText: "Удаление...",
            deletingFailedText: "Удалить не получилось"

        },
        display: {
            fileSizeOnSubmit: false
        },
        paste: {
            promptForName: false,
            namePromptMessage: "Please name this image"
        },
        showMessage: function(message){
            setTimeout(function() {
                window.alert(message);
            }, 0);
        },
        showConfirm: function(message, okCallback, cancelCallback) {
            setTimeout(function() {
                var result = window.confirm(message);
                if (result) {
                    okCallback();
                }
                else if (cancelCallback) {
                    cancelCallback();
                }
            }, 0);
        },
        showPrompt: function(message, defaultValue) {
            var promise = new qq.Promise(),
                retVal = window.prompt(message, defaultValue);

            /*jshint eqeqeq: true, eqnull: true*/
            if (retVal != null && qq.trimStr(retVal).length > 0) {
                promise.success(retVal);
            }
            else {
                promise.failure("Undefined or invalid user-supplied value.");
            }

            return promise;
        }
    }, true);

    // overwrite options with user supplied
    qq.extend(this._options, o, true);
    this._wrapCallbacks();

    // overwrite the upload button text if any
    // same for the Cancel button and Fail message text
    this._options.template     = this._options.template.replace(/\{dragZoneText\}/g, this._options.text.dragZone);
    this._options.template     = this._options.template.replace(/\{uploadButtonText\}/g, this._options.text.uploadButton);
    this._options.template     = this._options.template.replace(/\{dropProcessingText\}/g, this._options.text.dropProcessing);
    this._options.fileTemplate = this._options.fileTemplate.replace(/\{cancelButtonText\}/g, this._options.text.cancelButton);
    this._options.fileTemplate = this._options.fileTemplate.replace(/\{retryButtonText\}/g, this._options.text.retryButton);
    this._options.fileTemplate = this._options.fileTemplate.replace(/\{deleteButtonText\}/g, this._options.text.deleteButton);
    this._options.fileTemplate = this._options.fileTemplate.replace(/\{statusText\}/g, "");

    this._element = this._options.element;
    this._element.innerHTML = this._element.innerHTML + this._options.template;
    this._listElement = this._options.listElement || this._find(this._element, 'list');

    this._classes = this._options.classes;

    if (!this._button) {
        this._button = this._createUploadButton(this._find(this._element, 'button'));
    }

    this._bindCancelAndRetryEvents();

    this._dnd = this._setupDragAndDrop();

    if (this._options.paste.targetElement && this._options.paste.promptForName) {
        this._setupPastePrompt();
    }
};

// inherit from Basic Uploader
qq.extend(qq.FineUploader.prototype, qq.FineUploaderBasic.prototype);

qq.extend(qq.FineUploader.prototype, {
    clearStoredFiles: function() {
        qq.FineUploaderBasic.prototype.clearStoredFiles.apply(this, arguments);
        this._listElement.innerHTML = "";
    },
    addExtraDropzone: function(element){
        this._dnd.setupExtraDropzone(element);
    },
    removeExtraDropzone: function(element){
        return this._dnd.removeExtraDropzone(element);
    },
    getItemByFileId: function(id){
        var item = this._listElement.firstChild;

        // there can't be txt nodes in dynamically created list
        // and we can  use nextSibling
        while (item){
            if (item.qqFileId == id) return item;
            item = item.nextSibling;
        }
    },
    reset: function() {
        qq.FineUploaderBasic.prototype.reset.apply(this, arguments);
        this._element.innerHTML = this._options.template;
        this._listElement = this._options.listElement || this._find(this._element, 'list');
        if (!this._options.button) {
            this._button = this._createUploadButton(this._find(this._element, 'button'));
        }
        this._bindCancelAndRetryEvents();
        this._dnd.dispose();
        this._dnd = this._setupDragAndDrop();
    },
    _removeFileItem: function(fileId) {
        var item = this.getItemByFileId(fileId);
        $(item).remove();
    },
    _setupDragAndDrop: function() {
        var self = this,
            dropProcessingEl = this._find(this._element, 'dropProcessing'),
            dnd, preventSelectFiles, defaultDropAreaEl;

        preventSelectFiles = function(event) {
            event.preventDefault();
        };

        if (!this._options.dragAndDrop.disableDefaultDropzone) {
            defaultDropAreaEl = this._find(this._options.element, 'drop');
        }

        dnd = new qq.DragAndDrop({
            dropArea: defaultDropAreaEl,
            extraDropzones: this._options.dragAndDrop.extraDropzones,
            hideDropzones: this._options.dragAndDrop.hideDropzones,
            multiple: this._options.multiple,
            classes: {
                dropActive: this._options.classes.dropActive
            },
            callbacks: {
                dropProcessing: function(isProcessing, files) {
                    var input = self._button.getInput();

                    if (isProcessing) {
                        $(dropProcessingEl).css({display: 'block'});
                        qq(input).attach('click', preventSelectFiles);
                    }
                    else {
                        $(dropProcessingEl).hide();
                        qq(input).detach('click', preventSelectFiles);
                    }

                    if (files) {
                        self.addFiles(files);
                    }
                },
                error: function(code, filename) {
                    self._itemError(code, filename);
                },
                log: function(message, level) {
                    self.log(message, level);
                }
            }
        });

        dnd.setup();

        return dnd;
    },
    _leaving_document_out: function(e){
        return ((qq.chrome() || (qq.safari() && qq.windows())) && e.clientX == 0 && e.clientY == 0) // null coords for Chrome and Safari Windows
            || (qq.firefox() && !e.relatedTarget); // null e.relatedTarget for Firefox
    },
    _storeForLater: function(id) {
        qq.FineUploaderBasic.prototype._storeForLater.apply(this, arguments);
        var item = this.getItemByFileId(id);
        $(this._find(item, 'spinner')).hide();
    },
    /**
     * Gets one of the elements listed in this._options.classes
     **/
    _find: function(parent, type){
        var element = qq(parent).getByClass(this._options.classes[type])[0];
        if (!element){
            throw new Error('element not found ' + type);
        }

        return element;
    },
    _onSubmit: function(id, name){
        qq.FineUploaderBasic.prototype._onSubmit.apply(this, arguments);
        this._addToList(id, name);
    },
    // Update the progress bar & percentage as the file is uploaded
    _onProgress: function(id, name, loaded, total){
        qq.FineUploaderBasic.prototype._onProgress.apply(this, arguments);

        var item, progressBar, percent, cancelLink;

        item = this.getItemByFileId(id);
        progressBar = this._find(item, 'progressBar');
        percent = Math.round(loaded / total * 100);

        if (loaded === total) {
            cancelLink = this._find(item, 'cancel');
            $(cancelLink).hide();

            $(progressBar).hide();
            qq(this._find(item, 'statusText')).setText(this._options.text.waitingForResponse);

            // If last byte was sent, display total file size
            this._displayFileSize(id);
        }
        else {
            // If still uploading, display percentage - total size is actually the total request(s) size
            this._displayFileSize(id, loaded, total);

            $(progressBar).css({display: 'block'});
        }

        // Update progress bar element
        $(progressBar).css({width: percent + '%'});
    },
    _onComplete: function(id, name, result, xhr){
        qq.FineUploaderBasic.prototype._onComplete.apply(this, arguments);

        var item = this.getItemByFileId(id);
        if (this._options.display.completeFileDelete) {
            $(item).remove();
            return;
        }
        qq(this._find(item, 'statusText')).clearText();

        $(item).removeClass(this._classes.retrying);
        $(this._find(item, 'progressBar')).hide();

        if (!this._options.disableCancelForFormUploads || qq.isXhrUploadSupported()) {
            $(this._find(item, 'cancel')).hide();
        }
        $(this._find(item, 'spinner')).hide();

        if (result.success) {
            if (this._isDeletePossible()) {
                this._showDeleteLink(id);
            }
            if (result.double) {
                alert('Файл уже существует')
                $(this._find(item, 'deleteButton')).hide();
                $(this._find(item, 'retry')).hide();

                $(this._find(item, 'cancelNew')).show();
                $(this._find(item, 'upAndReload')).show();
                $(this._find(item, 'upNew')).show();
            }

            $(item).addClass(this._classes.success);
            if (this._classes.successIcon) {
                this._find(item, 'finished').style.display = "inline-block";
                $(item).addClass(this._classes.successIcon);
            }
        } else {
            $(item).addClass(this._classes.fail);
            if (this._classes.failIcon) {
                this._find(item, 'finished').style.display = "inline-block";
                $(item).addClass(this._classes.failIcon);
            }
            if (this._options.retry.showButton && !this._preventRetries[id]) {
                $(item).addClass(this._classes.retryable);
            }
            this._controlFailureTextDisplay(item, result);
        }
    },
    _onUpload: function(id, name){
        qq.FineUploaderBasic.prototype._onUpload.apply(this, arguments);

        this._showSpinner(id);
    },
    _onCancel: function(id, name) {
        qq.FineUploaderBasic.prototype._onCancel.apply(this, arguments);
        this._removeFileItem(id);
    },
    _onBeforeAutoRetry: function(id) {
        var item, progressBar, failTextEl, retryNumForDisplay, maxAuto, retryNote;

        qq.FineUploaderBasic.prototype._onBeforeAutoRetry.apply(this, arguments);

        item = this.getItemByFileId(id);
        progressBar = this._find(item, 'progressBar');

        this._showCancelLink(item);
        progressBar.style.width = 0;
        $(progressBar).hide();

        if (this._options.retry.showAutoRetryNote) {
            failTextEl = this._find(item, 'statusText');
            retryNumForDisplay = this._autoRetries[id] + 1;
            maxAuto = this._options.retry.maxAutoAttempts;

            retryNote = this._options.retry.autoRetryNote.replace(/\{retryNum\}/g, retryNumForDisplay);
            retryNote = retryNote.replace(/\{maxAuto\}/g, maxAuto);

            qq(failTextEl).setText(retryNote);
            if (retryNumForDisplay === 1) {
                $(item).addClass(this._classes.retrying);
            }
        }
    },
    //return false if we should not attempt the requested retry
    _onBeforeManualRetry: function(id) {
        var item = this.getItemByFileId(id);

        if (qq.FineUploaderBasic.prototype._onBeforeManualRetry.apply(this, arguments)) {
            this._find(item, 'progressBar').style.width = 0;
            $(item).removeClass(this._classes.fail);
            qq(this._find(item, 'statusText')).clearText();
            this._showSpinner(id);
            this._showCancelLink(item);
            return true;
        }
        else {
            $(item).addClass(this._classes.retryable);
            return false;
        }
    },
    _onSubmitDelete: function(id) {
        if (this._isDeletePossible()) {
            if (this._options.callbacks.onSubmitDelete(id) !== false) {
                if (this._options.deleteFile.forceConfirm) {
                    this._showDeleteConfirm(id);
                }
                else {
                    this._sendDeleteRequest(id);
                }
            }
        }
        else {
            this.log("Delete request ignored for file ID " + id + ", delete feature is disabled.", "warn");
            return false;
        }
    },
    _onDeleteComplete: function(id, xhr, isError) {
        qq.FineUploaderBasic.prototype._onDeleteComplete.apply(this, arguments);

        var item = this.getItemByFileId(id),
            spinnerEl = this._find(item, 'spinner'),
            statusTextEl = this._find(item, 'statusText');

        $(spinnerEl).hide();

        if (isError) {
            qq(statusTextEl).setText(this._options.deleteFile.deletingFailedText);
            this._showDeleteLink(id);
        }
        else {
            this._removeFileItem(id);
        }
    },
    _sendDeleteRequest: function(id) {
        var item = this.getItemByFileId(id),
            deleteLink = this._find(item, 'deleteButton'),
            statusTextEl = this._find(item, 'statusText');

        $(deleteLink).hide();
        this._showSpinner(id);
        qq(statusTextEl).setText(this._options.deleteFile.deletingStatusText);

        this._deleteHandler.sendDelete(id, this.getUuid(id));
    },
    _showDeleteConfirm: function(id) {
        var fileName = this._handler.getName(id),
            confirmMessage = this._options.deleteFile.confirmMessage.replace(/\{filename\}/g, fileName),
            uuid = this.getUuid(id),
            self = this;

        this._options.showConfirm(confirmMessage, function() {
            self._sendDeleteRequest(id);
        });
    },
    _addToList: function(id, name){
        var item = qq.toElement(this._options.fileTemplate);
        if (this._options.disableCancelForFormUploads && !qq.isXhrUploadSupported()) {
            var cancelLink = this._find(item, 'cancel');
            $(cancelLink).remove();
        }

        item.qqFileId = id;
        item.qqFileName = name

        var fileElement = this._find(item, 'file');
        qq(fileElement).setText(this._options.formatFileName(name));
        $(this._find(item, 'size')).hide();
        if (!this._options.multiple) {
            this._handler.cancelAll();
            this._clearList();
        }

        this._listElement.appendChild(item);

        if (this._options.display.fileSizeOnSubmit && qq.isXhrUploadSupported()) {
            this._displayFileSize(id);
        }
    },
    _clearList: function(){
        this._listElement.innerHTML = '';
        this.clearStoredFiles();
    },
    _displayFileSize: function(id, loadedSize, totalSize) {
        var item = this.getItemByFileId(id),
            size = this.getSize(id),
            sizeForDisplay = this._formatSize(size),
            sizeEl = this._find(item, 'size');

        if (loadedSize !== undefined && totalSize !== undefined) {
            sizeForDisplay = this._formatProgress(loadedSize, totalSize);
        }

        $(sizeEl).css({display: 'inline'});
        qq(sizeEl).setText(sizeForDisplay);
    },
    /**
     * delegate click event for cancel & retry links
     **/
    _bindCancelAndRetryEvents: function(){
        var self = this,
            list = this._listElement;
        var item = qq.toElement(this._options.fileTemplate);


        this._disposeSupport.attach(list, 'click', function(e){
            e = e || window.event;
            var target = e.target || e.srcElement;
            if ($(target).hasClass(self._classes.cancel) || $(target).hasClass(self._classes.retry) || $(target).hasClass(self._classes.deleteButton)|| $(target).hasClass(self._classes.cancelNew) || (target.classList[0] === 'qq-up-reup') || (target.classList[0] === 'qq-up')){
                qq.preventDefault(e);

                var item = target.parentNode.parentNode;
                while(item.qqFileId === undefined) {
                    item = target = target.parentNode;
                }

                if ($(target).hasClass(self._classes.deleteButton) || $(target).hasClass(self._classes.cancelNew)) {
                    self.deleteFile(item.qqFileId);
                }
                else if ($(target).hasClass(self._classes.cancel)) {
                    self.cancel(item.qqFileId);
                }

                else if (target.classList[0] === 'qq-up-reup'){
                   $.ajax({
                        url: '/ajax_up/',
                        data: item.qqFileName,
                        type: 'POST',
                        success: function (data){
                            $('.qq-up-reup').hide();
                            $('.qq-up').hide();
                            $('.qq-cancel').hide()
                            $('.qq-upload-delete').show();
                        }
                    })
            }
                else if (target.classList[0] === 'qq-up'){
                    $.ajax({
                        url: '/ajax_up_fasten/',
                        data: item.qqFileName,
                        type: 'POST',
                        success: function (data){
                            $('.qq-up-reup').hide();
                            $('.qq-up').hide();
                            $('.qq-cancel').hide()
                            $('.qq-upload-delete').show();
                        }
                    })
                }
                else {
                    $(item).removeClass(self._classes.retryable);
                    self.retry(item.qqFileId);
                }
            }

        });


    },
    _formatProgress: function (uploadedSize, totalSize) {
        var message = this._options.text.formatProgress;
        function r(name, replacement) { message = message.replace(name, replacement); }

        r('{percent}', Math.round(uploadedSize / totalSize * 100));
        r('{total_size}', this._formatSize(totalSize));
        return message;
    },
    _controlFailureTextDisplay: function(item, response) {
        var mode, maxChars, responseProperty, failureReason, shortFailureReason;

        mode = this._options.failedUploadTextDisplay.mode;
        maxChars = this._options.failedUploadTextDisplay.maxChars;
        responseProperty = this._options.failedUploadTextDisplay.responseProperty;

        if (mode === 'custom') {
            failureReason = response[responseProperty];
            if (failureReason) {
                if (failureReason.length > maxChars) {
                    shortFailureReason = failureReason.substring(0, maxChars) + '...';
                }
            }
            else {
                failureReason = this._options.text.failUpload;
                this.log("'" + responseProperty + "' is not a valid property on the server response.", 'warn');
            }

            qq(this._find(item, 'statusText')).setText(shortFailureReason || failureReason);

            if (this._options.failedUploadTextDisplay.enableTooltip) {
                this._showTooltip(item, failureReason);
            }
        }
        else if (mode === 'default') {
            qq(this._find(item, 'statusText')).setText(this._options.text.failUpload);
        }
        else if (mode !== 'none') {
            this.log("failedUploadTextDisplay.mode value of '" + mode + "' is not valid", 'warn');
        }
    },
    _showTooltip: function(item, text) {
        item.title = text;
    },
    _showSpinner: function(id) {
        var item = this.getItemByFileId(id),
            spinnerEl = this._find(item, 'spinner');

        spinnerEl.style.display = "inline-block";
    },
    _showCancelLink: function(item) {
        if (!this._options.disableCancelForFormUploads || qq.isXhrUploadSupported()) {
            var cancelLink = this._find(item, 'cancel');

            //qq(cancelLink).show();
        }
    },
    _showDeleteLink: function(id) {
        var item = this.getItemByFileId(id),
            deleteLink = this._find(item, 'deleteButton');

        //qq(deleteLink).show();
    },
    _itemError: function(code, name){
        var message = qq.FineUploaderBasic.prototype._itemError.apply(this, arguments);
        this._options.showMessage(message);
    },
    _batchError: function(message) {
        qq.FineUploaderBasic.prototype._batchError.apply(this, arguments);
        this._options.showMessage(message);
    },
    _setupPastePrompt: function() {
        var self = this;

        this._options.callbacks.onPasteReceived = function() {
            var message = self._options.paste.namePromptMessage,
                defaultVal = self._options.paste.defaultName;

            return self._options.showPrompt(message, defaultVal);
        };
    }
});
