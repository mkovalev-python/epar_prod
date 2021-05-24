/**
 * Created with PyCharm.
 * User: Gvammer
 * Date: 18.10.12
 * Time: 14:44
 * To change this template use File | Settings | File Templates.
 */

$(function(){
    var widget_ud = new widgetObject({id:'user_detail'});
    widget_ud.state = {
        taskCreate:false,
        hintOpened:{
            'Responsible':false,
            'Date':false,
            'Author':false
        }
    }
    widget_ud.container = $('#user_detail');

    $.extend(widget_ud,{
    });

    widget_ud.init();

    document.mainController.widgetsData["user_detail"] = widget_ud;

    $('.TabsMenu li').click(
        function(){
            $(this).addClass('Active').siblings().removeClass('Active');
            $('.TabsHolder .Block').removeClass('visible').filter('.'+$(this).attr('data-block')).addClass('visible');
            return false;
        }
    );
});