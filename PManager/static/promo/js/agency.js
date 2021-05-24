/*!
 * Start Bootstrap - Agency Bootstrap Theme (http://startbootstrap.com)
 * Code licensed under the Apache License v2.0.
 * For details, see http://www.apache.org/licenses/LICENSE-2.0.
 */
$(function() {
	var dp = jQuery;
	if (dp.fn.parallax) {
        //parallax on fullscreen slider
        dp.each(dp('.parallax-bg'), function(i) {
            var background = dp(this).data('background');
            dp(this).css({
                'background': 'url(' + background + ') 50% 0 / cover no-repeat',
                'background-attachment': 'fixed'
            });
        });
        dp('.parallax-bg').parallax("50%", 0.5);
    }
});


$(function() {
    $('a.page-scroll').bind('click', function(event) {
        var $anchor = $(this);
        $('html, body').stop().animate({
            scrollTop: $($anchor.attr('href')).offset().top
        }, 1500, 'easeInOutExpo');
        event.preventDefault();
    });
});

// Highlight the top nav as scrolling occurs
$('body').scrollspy({
    target: '.navbar-fixed-top'
})

// Closes the Responsive Menu on Menu Item Click
$('.navbar-collapse ul li a').click(function() {
    $('.navbar-toggle:visible').click();
});