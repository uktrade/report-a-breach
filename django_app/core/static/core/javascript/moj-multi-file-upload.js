function generateGuid() {
    return Math.random().toString(36).substring(2, 15) +
        Math.random().toString(36).substring(2, 15);
}


$.MultiFileUpload = function (params) {
    this.defaultParams = {
        uploadFileEntryHook: $.noop,
        uploadFileExitHook: $.noop,
        uploadFileErrorHook: $.noop,
        fileDeleteHook: $.noop,
        uploadStatusText: 'Uploading files, please wait',
        dropzoneHintText: 'Drag and drop files here or',
        dropzoneButtonText: 'Choose files'
    };

    this.params = $.extend({}, this.defaultParams, params);
    this.container = $(this.params.container);

    this.container.addClass('moj-multi-file-upload--enhanced');

    this.feedbackContainer = this.container.find('.moj-multi-file__uploaded-files');
    this.setupFileInput();
    this.setupDropzone();
    this.setupLabel();
    this.setupStatusBox();
    this.container.on('click', '.moj-multi-file-upload__delete', $.proxy(this, 'onFileDeleteClick'));
};

$.MultiFileUpload.prototype.setupDropzone = function () {
    this.fileInput.wrap('<div class="moj-multi-file-upload__dropzone" />');
    this.dropzone = this.container.find('.moj-multi-file-upload__dropzone');
    this.dropzone.on('dragover', $.proxy(this, 'onDragOver'));
    this.dropzone.on('dragleave', $.proxy(this, 'onDragLeave'));
    this.dropzone.on('drop', $.proxy(this, 'onDrop'));
};

$.MultiFileUpload.prototype.setupLabel = function () {
    this.label = $('<label for="' + this.fileInput[0].id + '" class="govuk-button govuk-button--secondary">' + this.params.dropzoneButtonText + '</label>');
    this.dropzone.append('<p class="govuk-body">' + this.params.dropzoneHintText + '</p>');
    this.dropzone.append(this.label);
};

$.MultiFileUpload.prototype.setupFileInput = function () {
    this.fileInput = this.container.find('.moj-multi-file-upload__input');
    this.fileInput.on('change', $.proxy(this, 'onFileChange'));
    this.fileInput.on('focus', $.proxy(this, 'onFileFocus'));
    this.fileInput.on('blur', $.proxy(this, 'onFileBlur'));
};

$.MultiFileUpload.prototype.setupStatusBox = function () {
    this.status = $('<div aria-live="polite" role="status" class="govuk-visually-hidden" />');
    this.dropzone.append(this.status);
};

$.MultiFileUpload.prototype.onDragOver = function (e) {
    e.preventDefault();
    this.dropzone.addClass('moj-multi-file-upload--dragover');
};

$.MultiFileUpload.prototype.onDragLeave = function () {
    this.dropzone.removeClass('moj-multi-file-upload--dragover');
};

$.MultiFileUpload.prototype.onDrop = function (e) {
    e.preventDefault();
    this.dropzone.removeClass('moj-multi-file-upload--dragover');
    this.feedbackContainer.removeClass('moj-hidden');
    this.status.html(this.params.uploadStatusText);
    this.uploadFiles(e.originalEvent.dataTransfer.files);
};

$.MultiFileUpload.prototype.uploadFiles = function (files) {
    for (var i = 0; i < files.length; i++) {
        this.uploadFile(files[i]);
    }
};

$.MultiFileUpload.prototype.onFileChange = function (e) {
    this.feedbackContainer.removeClass('moj-hidden');
    this.status.html(this.params.uploadStatusText);
    this.uploadFiles(e.currentTarget.files);
    this.fileInput.replaceWith($(e.currentTarget).val('').clone(true));
    this.setupFileInput();
    this.fileInput.focus();
};

$.MultiFileUpload.prototype.onFileFocus = function (e) {
    this.label.addClass('moj-multi-file-upload--focused');
};

$.MultiFileUpload.prototype.onFileBlur = function (e) {
    this.label.removeClass('moj-multi-file-upload--focused');
};

$.MultiFileUpload.prototype.getSuccessHtml = function (file_name, file_url) {
    var html = ''
    html += '<span class="moj-multi-file-upload__filename">'
    html +=  file_name
    html += '</span>'

    return html;
};

$.MultiFileUpload.prototype.getErrorHtml = function (response) {
    let id = generateGuid()

    var html = ''
    html += '<div class="govuk-form-group govuk-form-group--error">'
    html += '<span class="moj-multi-file-upload__filename">' + response.file_name + '</span>';
    html += '<br><br>'
    html += '<span class="moj-multi-file-upload__error">'
    html += response.error
    html += '</span>'
    html += '<br><br>'
    html += '<input id="' + id + '" type="file" name="upload_documents-document" class="file-upload-error-input hidden">'
    html += '<label for="' + id + '" class="govuk-button govuk-button--secondary">Choose file</label>'
    html += '</div>'
    return html
};


$.MultiFileUpload.prototype.getErrorSummaryHtml = function (error, input_id) {
    var html = ''

    html += '<div class="govuk-error-summary" aria-labelledby="error-summary-title" role="alert" tabindex="-1"  data-module="govuk-error-summary">'
    html += '<h2 class="govuk-error-summary__title" id="error-summary-title">There is a problem</h2>'
    html += '<div class="govuk-error-summary__body">'
    html += '<ul class="govuk-list govuk-error-summary__list">'

    html += this.getErrorSummaryListElementHtml(error, input_id)

    html += '</ul>'
    html += '</div>'
    html += '</div>'

    return html
};

$.MultiFileUpload.prototype.getErrorSummaryListElementHtml = function (error, input_id) {
    return '<li><a href="#' + input_id + '">' + error + '</a></li>'
};


$.MultiFileUpload.prototype.deleteErrorSummaryListElement = function (row_id) {
    // delete the corresponding error summary list element
    $('.govuk-error-summary__list').find(`a[href="#${row_id}"]`).parent().remove();

    // If the summary list is empty, remove the error summary box
    if ($('.govuk-error-summary__list').children().length === 0) {
        $('.govuk-error-summary').remove();
    }
};


$.MultiFileUpload.prototype.getFileRowHtml = function (file) {
    var html = '';
    html += '<div class="govuk-summary-list__row moj-multi-file-upload__row">';
    html += '  <div class="govuk-summary-list__value moj-multi-file-upload__message">';
    html += '<span class="moj-multi-file-upload__filename">' + file.name + '</span>';
    html += '<span class="moj-multi-file-upload__progress">0%</span>';
    html += '  </div>';
    html += '  <div class="govuk-summary-list__actions moj-multi-file-upload__actions"></div>';
    html += '</div>';
    return html;
};

$.MultiFileUpload.prototype.getDeleteButtonHtml = function (file_name) {
    var html = '<a class="moj-multi-file-upload__delete govuk-!-margin-bottom-0" href="javascript:void(0)" data-file-name="' + file_name + '">';
    html += 'Remove <span class="govuk-visually-hidden">' + file_name + '</span>';
    html += '</a>';
    return html;
};

$.MultiFileUpload.prototype.uploadFile = function (file) {
    this.params.uploadFileEntryHook(this, file);
    var formData = new FormData();
    formData.append('document', file);
    var item = $(this.getFileRowHtml(file));
    this.feedbackContainer.find('.moj-multi-file-upload__list').append(item);

    // Show the uploaded files container
    var token = $('input[name="csrfmiddlewaretoken"]').attr('value');
    $.ajax({
        url: this.params.uploadUrl,
        type: 'post',
        data: formData,
        headers: {
            'X-CSRFToken': token
        },
        processData: false,
        contentType: false,
        success: $.proxy(function (response) {
            if (response.success) {
                item.find('.moj-multi-file-upload__message').html(this.getSuccessHtml(response.file_name, response.file_url));
                this.status.html("Success");

            } else {
                item.find('.moj-multi-file-upload__message').html(this.getErrorHtml(response));

                let id = item.attr("id")
                if (typeof id === 'undefined' || id === false) {
                    id = generateGuid()
                    item.prop("id", id)
                }

                // Error summary handling
                if ($('.govuk-error-summary__list').length) {
                    // We have an error summary box already
                    $('.govuk-error-summary__list').last().append(this.getErrorSummaryListElementHtml(response.error, id));
                } else {
                    // We need to create an error summary box
                    $('.govuk-grid-column-two-thirds').last().prepend(this.getErrorSummaryHtml(response.error, id))
                }
            }
            item.find('.moj-multi-file-upload__actions').append(this.getDeleteButtonHtml(response.file_name));
            this.params.uploadFileExitHook(this, file, response);
        }, this),
        error: $.proxy(function (jqXHR, textStatus, errorThrown) {
            this.params.uploadFileErrorHook(this, file, jqXHR, textStatus, errorThrown);
            item.remove()
        }, this),
        xhr: function () {
            var xhr = new XMLHttpRequest();
            xhr.upload.addEventListener('progress', function (e) {
                if (e.lengthComputable) {
                    var percentComplete = e.loaded / e.total;
                    percentComplete = parseInt(percentComplete * 100, 10);
                    item.find('.moj-multi-file-upload__progress').text(' ' + percentComplete + '%');

                }
            }, false);
            return xhr;
        }
    });
};

$.MultiFileUpload.prototype.onFileDeleteClick = function (e) {
    e.preventDefault(); // if user refreshes page and then deletes
    var delete_link = $(e.currentTarget);
    let file_name = delete_link.data('file-name');
    var token = $('input[name="csrfmiddlewaretoken"]').attr('value');
    $.ajax({
        url: this.params.deleteUrl + "?file_name=" + file_name,
        type: 'post',
        dataType: 'json',
        headers: {
            'X-CSRFToken': token
        },
        success: $.proxy(function (response) {
            if (response.error) {
                // handle error
            } else { // delete the row
                let parent_row = delete_link.parents('.moj-multi-file-upload__row').remove();

                // first check if there were any error summaries associated with this row, if so, delete them
                if (parent_row.find('input.file-upload-error-input').length) {
                    let row_id = parent_row.attr('id')
                    this.deleteErrorSummaryListElement(row_id)
                }

                // hide the feedback container if there are no more rows
                if (this.feedbackContainer.find('.moj-multi-file-upload__row').length === 0) {
                    this.feedbackContainer.addClass('moj-hidden');
                }
            }
            this.params.fileDeleteHook(this, response);
        }, this)
    });
};
