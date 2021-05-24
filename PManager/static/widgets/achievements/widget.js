/**
 * Created with PyCharm.
 * User: Gvammer
 * Date: 18.10.12
 * Time: 14:44
 * To change this template use File | Settings | File Templates.
 */

$(function(){
    var widget_ac = new widgetObject({id:'achivements'});
    widget_ac.state = {
        taskCreate:false,
        hintOpened:{
            'Responsible':false,
            'Date':false,
            'Author':false
        }
    }
    widget_ac.container = $('#achivements');

    $.extend(widget_ac,{
    });

    widget_ac.init();

    document.mainController.widgetsData["achivements"] = widget_ac;
});