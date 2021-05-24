$(function(){
    var userList = new widgetObject({id:'userList'});
    $.extend(userList, {
        'init':function(){
            this.userBlockSelector = '.js-user';
            this.addStatusListeners();
        },
        'addStatusListeners': function(){
            var widget = this;
            baseConnector.addListener('connect', function(){
                widget.setOnlineStatusFromServer();
                if (widget.statusInterval) clearInterval(widget.statusInterval);
                widget.statusInterval = setInterval(function(){
                    widget.setOnlineStatusFromServer();
                }, 5000)
            });
            baseConnector.addListener('userLogin', function(userData){
                widget.setUserStatus(userData.id, {
                    'status':'online'
                })
            });
        },
        '$getUserBlocks': function(){
            return $(this.userBlockSelector);
        },
        'setUserStatus': function(id, data){
            var $userBlock = $(this.userBlockSelector).filter('[data-id='+id+']');
            if (data.status)
                $userBlock.attr('data-status', data.status);
        },
        "setOnlineStatusFromServer": function(){
            var widget = this;
            var $userBlocks = widget.$getUserBlocks();
            baseConnector.addListener('users:online', function(receivedUsers){
                var aUsersOnline = $.parseJSON(receivedUsers);
                for (var i in aUsersOnline) {
                    var aUserStatus = aUsersOnline[i];
                    widget.setUserStatus(aUserStatus['id'], aUserStatus);
                    $userBlocks = $userBlocks.not('[data-id='+aUserStatus['id']+']');
                }

                $userBlocks.each(function(){
                    widget.setUserStatus($(this).data('id'), {
                        'status':'offline'
                    });
                });
            });
            baseConnector.send("users:get_online_list", {
                    'data':'test'
                }
            );
        }
    });
    userList.init();
});
