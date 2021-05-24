;$(function(){
    var JS_NAV_TAB_FIRST = '.nav-tabs a:first',
        JS_NAV_DATA_TAB = 'a[data-toggle="tab"]';

    window.addEventListener("popstate", function(e) {
        var activeTab = $('[href=' + location.hash + ']');
        if (activeTab.length) {
            activeTab.tab('show');
        } else {
            $(JS_NAV_TAB_FIRST).tab('show');
        }
    });
    if (location.hash) {
        var activeTab = $('[href=' + location.hash + ']');
        if (activeTab.get(0)) {
            activeTab.tab('show');
        }
    }
    $(JS_NAV_DATA_TAB).on('click', function(e) {
        history.pushState(null, null, $(this).attr('href'));
    });

});