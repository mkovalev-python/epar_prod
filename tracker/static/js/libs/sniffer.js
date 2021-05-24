/**
 * Created by tracker_maker on 02.07.15.
 */

var Sniffer = {
    'getErrors': function(path, author, project) {
        PM_AjaxPost(
            '/sniffer/get_errors/',
            {
                'path': path,
                'user': author,
                'project': project
            },
            function(data){
                $('<div class="modal fade js-set-deadline green-popup" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true" >' +
                    '<div class="modal-dialog"><div class="modal-content"><div class="modal-header"><button type="button" class="close" data-dismiss="modal" aria-label="Close"><spanaria-hidden="true">&times;</span></button><h3 class="modal-title">'+path+'</h3>' +
                        '</div><div class="modal-body clearfix deadline-wrapper"></div>' +
                            '<div class="modal-footer">' +
                                '<button type="button" class="btn btn-danger" data-dismiss="modal">Закрыть</button>' +
                            '</div>' +
                        '</div>' +
                    '</div>' +
                  '</div>' +
                '</div>')
				.find('.modal-body')
				.append(data).end().modal('show');
            }
        );
        return false;
    }
};