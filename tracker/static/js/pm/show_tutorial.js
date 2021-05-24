function showTutorial () {
    $('body').addClass('first-task-slider');
    $.fancybox.open(
        [
            //{href: "/static/images/start_slider/first.jpg"},
            //{href: "/static/images/start_slider/apprice.jpg"},
            //{href: "/static/images/start_slider/ctrlv.jpg"}
            {href: "/static/images/start_slider/slide1.jpg"},
            {href: "/static/images/start_slider/slide2.jpg"},
            {href: "/static/images/start_slider/slide3.jpg"},
            {href: "/static/images/start_slider/slide4.jpg"}
        ],
        {
            helpers : {
                overlay : {
                    css : {
                        'background' : 'rgba(255, 255, 255, 0.6)'
                    }
                }
            },
            openEffect  : 'none',
            closeEffect : 'none',
            nextEffect  : 'none',
            prevEffect  : 'none',
            padding     : 0,
            margin      : [20, 60, 20, 60],
            width:700,
            height:470
        }
    )   
}  