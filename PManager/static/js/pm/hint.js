/**
 * Created with PyCharm.
 * User: Gvammer
 * Date: 07.06.13
 * Time: 18:23
 */
var ajaxNoticeUrl = '/ajax/notice';

var hintObject = function(data){
    this.title = data.title;
    this.text = data.text;
    this.image = data.image;
    this.id = data.id;
    this.init();
}

hintObject.prototype = {
    'init':function(){
        var template = this.template();
        template = template.replace('#TITLE#',this.title);
        template = template.replace('#TEXT#',this.text);
        template = template.replace('#IMAGE#',this.image);

        this.$container = $(template).appendTo('body');
        if (!this.image){
            this.$container.find('img').remove();
        }
    },
    'remove': function(){
        this.$container.remove();
    },
    'template':function(){
        return '<div class="project_hint" style="display:none;">' +
                    '<img src="#IMAGE#" />' +
                    '<h5>#TITLE#</h5>' +
                    '<p>#TEXT#</p>' +
                    '<div class="clr"></div>' +
//                        '<a href="#" class="hint-more">read more!</a>' +
            '</div>';
    },
    'show': function(object){
        if (!object) return false;

        this.registerUserView();
        var targetPosition = getObjectCenterPos(object), classH, cssObj;
        var popupWidth = this.$container.width(), popupHeight = this.$container.height();

        if (targetPosition.left - popupWidth > 0){
                if(targetPosition.top - popupHeight < 0){
                    classH = 'top';
                    cssObj = {
                        'left':targetPosition.left - (popupWidth/2) - 6,
                        'top':targetPosition.top + targetPosition.height + 4
                    }
                }else{
                    classH = 'right';
                    cssObj = {
                        'left':targetPosition.left - popupWidth - 34,
                        'top':targetPosition.top - (popupHeight/2) - 6
                    }
                }
        }else if(targetPosition.left + targetPosition.width + this.$container.width() < $(window).width()){
            classH = 'left';
            cssObj = {
                'left':targetPosition.left + targetPosition.width + 4,
                'top':targetPosition.top - (popupHeight/2) - 6
            }
        }else{
            if(targetPosition.top < popupHeight){
                classH = 'bottom';
                cssObj = {
                    'left':targetPosition.left + targetPosition.width/2 - this.$container.width()/2 + 4,
                    'top':targetPosition.top - (popupHeight) - 34
                }
            }else{
                classH = 'top';
                cssObj = {
                    'left':targetPosition.left + targetPosition.width/2 - this.$container.width()/2 + 4,
                    'top':targetPosition.top + (targetPosition.height)
                }
            }
        }
        this.$container.addClass(classH)
                        .css(cssObj)
                        .show()
                        .click(function(e){
                            e.stopPropagation();
                        });

        var t = this;
        $(document).one('click',function(){
            t.remove();
        });
        return this;
    },
    'registerUserView': function(){
        if (this.id){
            PM_AjaxPost(ajaxNoticeUrl,{
                'id':this.id
            },function(){

            });
        }
    }
}