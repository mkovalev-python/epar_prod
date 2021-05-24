var MIN_WIDTH_FOR_TASK_LINES = 992;
(function($) {
    //BROWSER INCLUDE START
    var matched, browser;

    // Use of jQuery.browser is frowned upon.
    // More details: http://api.jquery.com/jQuery.browser
    // jQuery.uaMatch maintained for back-compat
    jQuery.uaMatch = function( ua ) {
        ua = ua.toLowerCase();

        var match = /(chrome)[ \/]([\w.]+)/.exec( ua ) ||
            /(webkit)[ \/]([\w.]+)/.exec( ua ) ||
            /(opera)(?:.*version|)[ \/]([\w.]+)/.exec( ua ) ||
            /(msie) ([\w.]+)/.exec( ua ) ||
            ua.indexOf("compatible") < 0 && /(mozilla)(?:.*? rv:([\w.]+)|)/.exec( ua ) ||
            [];

        return {
            browser: match[ 1 ] || "",
            version: match[ 2 ] || "0"
        };
    };

    matched = jQuery.uaMatch( navigator.userAgent );
    browser = {};

    if ( matched.browser ) {
        browser[ matched.browser ] = true;
        browser.version = matched.version;
    }

    // Chrome is Webkit, but Webkit is also Safari.
    if ( browser.chrome ) {
        browser.webkit = true;
    } else if ( browser.webkit ) {
        browser.safari = true;
    }

    $.browser = browser;
    ///////BROWSER INCLUDE END
    $(function() {
        function createCookie(name,value,days) {
            if (days) {
                var date = new Date();
                date.setTime(date.getTime()+(days*24*60*60*1000));
                var expires = "; expires="+date.toGMTString();
            }
            else var expires = "";
            document.cookie = name+"="+value+expires+"; path=/";
        }
        function readCookie(name) {
            var nameEQ = name + "=";
            var ca = document.cookie.split(';');
            for(var i=0;i < ca.length;i++) {
                var c = ca[i];
                while (c.charAt(0)==' ') c = c.substring(1,c.length);
                if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
            }
            return null;
        }
        function eraseCookie(name) {
            createCookie(name,"",-1);
        }

        $('.ViewText .Hide').hide();

        $('.FilterBlock .Hide').hide();
        $('.FilterBlock a.HideText').toggle(
         function(){
            $(this).siblings('.Hide').stop(false, true).slideDown(0);
            $(this).html('<a class="hideFilter" href="#">свернуть фильтр</a>');
         },
         function(){
            $(this).siblings('.Hide').stop(false, true).slideUp(0);
            $(this).html('<a class="showFilter" href="#">развернуть фильтр</a>');
         });

         $('div.AllMessageLink').toggle(function() {
         $(this).siblings('div').stop(false, true).slideDown('0');
            $(this).html('<span>Спрятать сообщения</span>');
         }, function() {
         $(this).siblings('div').stop(false, true).slideUp('0');
            $(this).html('<span>Показать все сообщения</span>');
         return false;
        });

        if (!$.cookie('open_task_requested')) {
            if (oMyCurrentTimer && !oMyCurrentTimer.started) {
                userDynamics.getOpenTask();
                $.cookie('open_task_requested', 'Y', { expires: 1});
            }
        }
    });
})(jQuery);

function fixEvent(e) {
    // получить объект событие для IE
    e = e || window.event;

    // добавить pageX/pageY для IE
    if ( e.pageX == null && e.clientX != null ) {
        var html = document.documentElement;
        var body = document.body;
        e.pageX = e.clientX + (html && html.scrollLeft || body && body.scrollLeft || 0) - (html.clientLeft || 0);
        e.pageY = e.clientY + (html && html.scrollTop || body && body.scrollTop || 0) - (html.clientTop || 0);
    }

    // добавить which для IE
    if (!e.which && e.button) {
        e.which = e.button & 1 ? 1 : ( e.button & 2 ? 3 : ( e.button & 4 ? 2 : 0 ) )
    }

    return e
}
function htmlspecialchars_decode (string, quote_style) {
    // http://kevin.vanzonneveld.net
    // +   original by: Mirek Slugen
    // +   improved by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
    // +   bugfixed by: Mateusz "loonquawl" Zalega
    // +      input by: ReverseSyntax
    // +      input by: Slawomir Kaniecki
    // +      input by: Scott Cariss
    // +      input by: Francois
    // +   bugfixed by: Onno Marsman
    // +    revised by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
    // +   bugfixed by: Brett Zamir (http://brett-zamir.me)
    // +      input by: Ratheous
    // +      input by: Mailfaker (http://www.weedem.fr/)
    // +      reimplemented by: Brett Zamir (http://brett-zamir.me)
    // +    bugfixed by: Brett Zamir (http://brett-zamir.me)
    // *     example 1: htmlspecialchars_decode("<p>this -&gt; &quot;</p>", 'ENT_NOQUOTES');
    // *     returns 1: '<p>this -> &quot;</p>'
    // *     example 2: htmlspecialchars_decode("&amp;quot;");
    // *     returns 2: '&quot;'
    var optTemp = 0,
        i = 0,
        noquotes = false;
    if (typeof quote_style === 'undefined') {
        quote_style = 2;
    }
    string = string.toString().replace(/&lt;/g, '<').replace(/&gt;/g, '>');
    var OPTS = {
        'ENT_NOQUOTES': 0,
        'ENT_HTML_QUOTE_SINGLE': 1,
        'ENT_HTML_QUOTE_DOUBLE': 2,
        'ENT_COMPAT': 2,
        'ENT_QUOTES': 3,
        'ENT_IGNORE': 4
    };
    if (quote_style === 0) {
        noquotes = true;
    }
    if (typeof quote_style !== 'number') { // Allow for a single string or an array of string flags
        quote_style = [].concat(quote_style);
        for (i = 0; i < quote_style.length; i++) {
            // Resolve string input to bitwise e.g. 'PATHINFO_EXTENSION' becomes 4
            if (OPTS[quote_style[i]] === 0) {
                noquotes = true;
            } else if (OPTS[quote_style[i]]) {
                optTemp = optTemp | OPTS[quote_style[i]];
            }
        }
        quote_style = optTemp;
    }
    if (quote_style & OPTS.ENT_HTML_QUOTE_SINGLE) {
        string = string.replace(/&#0*39;/g, "'"); // PHP doesn't currently escape if more than one 0, but it should
        // string = string.replace(/&apos;|&#x0*27;/g, "'"); // This would also be useful here, but not a part of PHP
    }
    if (!noquotes) {
        string = string.replace(/&quot;/g, '"');
    }
    // Put this in last place to avoid escape being double-decoded
    string = string.replace(/&amp;/g, '&');

    return string;
}
function randomString(string_length) {
    if (!string_length)
        string_length = 8;

    var chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXTZabcdefghiklmnopqrstuvwxyz";
    var randomstring = '';

    for (var i=0; i<string_length; i++) {
        var rnum = Math.floor(Math.random() * chars.length);
        randomstring += chars.substring(rnum, rnum+1);
    }

    return randomstring;
}
//function setTaskCellsHeight($object){
//	return true;
//    if (!$object){
//        $object = $('.task');
//    }
//    var winWidth = $(window).width();
//    $object.each(function(){
//
//        $(this).children().children().each(function(){
//            $(this).css('height', '');
//        });
//        var height = $(this).height();
//        //task cells height
//        if (winWidth > MIN_WIDTH_FOR_TASK_LINES){
//            $(this).children().children().each(function(){
//                    $(this).height(height - 10);
//            });
//        }
//    });
//}
var GLOBAL_RESIZE_TIMER = false;
function setTaskCellsHeight($object){
    if (!$object){
        $object = $('.task');
    }
    if (GLOBAL_RESIZE_TIMER) clearTimeout(GLOBAL_RESIZE_TIMER);
    GLOBAL_RESIZE_TIMER = setTimeout(function(){
        $object.each(function(){
            $(this).find('.task-drag').css('height', $(this).height()+1);//task-drag have margin -1 for hide top border of task
         });
    }, 200);
}

function getIconForExtension(extension) {
    if (extension == 'doc' || extension == 'docx')
        return 'word';
    else if (extension == 'xls' || extension == 'xlsx')
        return 'excel';
    else if (extension == 'pdf')
        return 'pdf';
    else if (extension == 'zip' || extension == 'rar')
        return 'archive';
    else
        return false;
}

$(function(){
    $(window).resize(function() {
        setTaskCellsHeight();
    });

    $(document).on('click', '.fnc', function(){
        $.fancybox({
            'href': $(this).attr('href')
        });
        return false;
    }).on('click', '.fnc_ajax', function(){
        $.fancybox({
            'href': $(this).attr('href'),
            'type': 'ajax'
        });
        return false;
    }).on('click', '.w-close', function(){
        $(this).closest('.widget').remove();
    });

    $('.js-phone').mask('+7 (999) 999-99-99');
});