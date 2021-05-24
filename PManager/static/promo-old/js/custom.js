/* =================================
   LOADER                     
=================================== */
// makes sure the whole site is loaded
jQuery(window).load(function() {
        // will first fade out the loading animation
	jQuery(".status").fadeOut();
        // will fade out the whole DIV that covers the website.
	jQuery(".preloader").delay(1000).fadeOut("slow");
})

/* =================================
===  RESPONSIVE VIDEO           ====
=================================== */

$(".video-container").fitVids();


/* =================================
===  MAILCHIMP                 ====
=================================== */

//$('.mailchimp').ajaxChimp({
//    callback: mailchimpCallback,
//    url: "http://webdesign7.us6.list-manage.com/subscribe/post?u=9445a2e155b82208d73433060&amp;id=16dc80e353" //Replace this with your own mailchimp post URL. Don't remove the "". Just paste the url inside "".
//});

function mailchimpCallback(resp) {
     if (resp.result === 'success') {
        $('.subscription-success').html('<i class="icon_check_alt2"></i><br/>' + resp.msg).fadeIn(1000);
        $('.subscription-error').fadeOut(500);
        
    } else if(resp.result === 'error') {
        $('.subscription-error').html('<i class="icon_close_alt2"></i><br/>' + resp.msg).fadeIn(1000);
    }  
}

/* =================================
===  STICKY NAV                 ====
=================================== */

$(document).ready(function() {
  $('.main-navigation').onePageNav({
    scrollThreshold: 0.2, // Adjust if Navigation highlights too early or too late
    filter: ':not(.external)',
    changeHash: true
  });
  
});


/* COLLAPSE NAVIGATION ON MOBILE AFTER CLICKING ON LINK - ADDED ON V1.5*/

if (matchMedia('(max-width: 480px)').matches) {
    $('.main-navigation a').on('click', function () {
        $(".navbar-toggle").click();
    });
}

/* =================================
===  DOWNLOAD BUTTON CLICK SCROLL ==
=================================== */
jQuery(function( $ ){
			$('#download-button').localScroll({
				duration:1000
			});
		});


/* =================================
===  FULL SCREEN HEADER         ====
=================================== */
function alturaMaxima() {
  var altura = $(window).height();
  $(".full-screen").css('min-height',altura); 
  
}

$(document).ready(function() {
  alturaMaxima();
  $(window).bind('resize', alturaMaxima);
});


/* =================================
===  SMOOTH SCROLL             ====
=================================== */
var scrollAnimationTime = 1200,
    scrollAnimation = 'easeInOutExpo';
$('a.scrollto').bind('click.smoothscroll', function (event) {
    event.preventDefault();
    var target = this.hash;
    $('html, body').stop().animate({
        'scrollTop': $(target).offset().top
    }, scrollAnimationTime, scrollAnimation, function () {
        window.location.hash = target;
    });
});


/* =================================
===  WOW ANIMATION             ====
=================================== */
wow = new WOW(
  {
    mobile: false
  });
wow.init();


/* =================================
===  OWL CROUSEL               ====
=================================== */
$(document).ready(function () {

    $("#feedbacks").owlCarousel({

        navigation: false, // Show next and prev buttons
        slideSpeed: 400,
        paginationSpeed: 800,
        autoPlay: 10000,
        singleItem: true

    });

    var owl = $("#screenshots");

    owl.owlCarousel({
        items: 1, //10 items above 1000px browser width
        itemsDesktop: [1000, 1], //5 items between 1000px and 901px
        itemsDesktopSmall: [900, 1], // betweem 900px and 601px
        itemsTablet: [600, 1], //2 items between 600 and 0
        itemsMobile: false // itemsMobile disabled - inherit from itemsTablet option
    });

    $(".next").click(function(){
        owl.trigger('owl.next');
    });
    $(".prev").click(function(){
        owl.trigger('owl.prev');
    })
});


/* =================================
===  Nivo Lightbox              ====
=================================== */
$(document).ready(function () {

    $('#screenshots a').nivoLightbox({
        effect: 'fadeScale'
    });

});


/* =================================
===  SUBSCRIPTION FORM          ====
=================================== */
$("#subscribe").submit(function (e) {
    e.preventDefault();
    var email = $("#subscriber-email").val();
    var dataString = 'email=' + email;

    function isValidEmail(emailAddress) {
        var pattern = new RegExp(/^((([a-z]|\d|[!#\$%&'\*\+\-\/=\?\^_`{\|}~]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])+(\.([a-z]|\d|[!#\$%&'\*\+\-\/=\?\^_`{\|}~]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])+)*)|((\x22)((((\x20|\x09)*(\x0d\x0a))?(\x20|\x09)+)?(([\x01-\x08\x0b\x0c\x0e-\x1f\x7f]|\x21|[\x23-\x5b]|[\x5d-\x7e]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(\\([\x01-\x09\x0b\x0c\x0d-\x7f]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]))))*(((\x20|\x09)*(\x0d\x0a))?(\x20|\x09)+)?(\x22)))@((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?$/i);
        return pattern.test(emailAddress);
    };

    if (isValidEmail(email)) {
        $.ajax({
            type: "POST",
            url: "subscribe/subscribe.php",
            data: dataString,
            success: function () {
                $('.subscription-success').fadeIn(1000);
                $('.subscription-error').fadeOut(500);
                $('.hide-after').fadeOut(500);
            }
        });
    } else {
        $('.subscription-error').fadeIn(1000);
    }

    return false;
});



/* =================================
===  CONTACT FORM          ====
=================================== */
$("#contact").submit(function (e) {
    e.preventDefault();
    var name = $("#name").val();
    var email = $("#email").val();
    var subject = $("#subject").val();
    var message = $("#message").val();
    var dataString = 'name=' + name + '&email=' + email + '&subject=' + subject + '&message=' + message;

    function isValidEmail(emailAddress) {
        var pattern = new RegExp(/^((([a-z]|\d|[!#\$%&'\*\+\-\/=\?\^_`{\|}~]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])+(\.([a-z]|\d|[!#\$%&'\*\+\-\/=\?\^_`{\|}~]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])+)*)|((\x22)((((\x20|\x09)*(\x0d\x0a))?(\x20|\x09)+)?(([\x01-\x08\x0b\x0c\x0e-\x1f\x7f]|\x21|[\x23-\x5b]|[\x5d-\x7e]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(\\([\x01-\x09\x0b\x0c\x0d-\x7f]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]))))*(((\x20|\x09)*(\x0d\x0a))?(\x20|\x09)+)?(\x22)))@((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?$/i);
        return pattern.test(emailAddress);
    };

    if (isValidEmail(email) && (message.length > 1) && (name.length > 1)) {
        $.ajax({
            type: "POST",
            url: "/sendmail/",
            data: dataString,
            success: function () {
                $('.success').fadeIn(1000);
                $('.error').fadeOut(500);
            }
        });
    } else {
        $('.error').fadeIn(1000);
        $('.success').fadeOut(500);
    }

    return false;
});



/* =================================
===  EXPAND COLLAPSE            ====
=================================== */
$('.expand-form').simpleexpand({
    'defaultTarget': '.expanded-contact-form'
});



/* =================================
===  STELLAR                    ====
=================================== */
$(window).stellar({ 
horizontalScrolling: false 
});



/* =================================
===  Bootstrap Internet Explorer 10 in Windows 8 and Windows Phone 8 FIX
=================================== */
if (navigator.userAgent.match(/IEMobile\/10\.0/)) {
  var msViewportStyle = document.createElement('style');
  msViewportStyle.appendChild(
    document.createTextNode(
      '@-ms-viewport{width:auto!important}'
    )
  );
  document.querySelector('head').appendChild(msViewportStyle)
}

$(function () {
    $('.color-overlay').css('min-height', $(window).height());

    $(document).click(function(e){
        $('.js-select-responsible').hide();
    });

    $('.js-demo-browser-block').on('click', '.js-gear', function () {
        $(this).find('.js-menu').toggle();
        return false;
    })
            .on('click', '.js-close-task', function () {
                $('[data-id="' + $(this).closest('.js-task-block').data('id') + '"]').toggleClass('closed');
                return false;
            })
            .on('click', '.js-set-task-ready', function () {
                var $task = $('[data-id="' + $(this).closest('.js-task-block').data('id') + '"]').toggleClass('ready');
                if ($task.hasClass('ready')) {
                    $task.find('.js-set-ready').text('На доработку');
                } else {
                    $task.find('.js-set-ready').text('На доработку');
                }
            })
            .on('click', '.js-play', function() {
                if ($(this).hasClass('fa-play-circle')) {
                    $(this).add('[data-id="'+$(this).closest('.js-task-block').data('id')+'"] .js-play').removeClass('fa-play-circle').addClass('fa-pause')
                            .parent().removeClass('play').addClass('pause').end()
                            .each(function(){$(this).closest('.js-task-block').data('timer').start()});
                } else {
                    $(this).add('[data-id="'+$(this).closest('.js-task-block').data('id')+'"] .js-play').removeClass('fa-pause').addClass('fa-play-circle')
                            .parent().removeClass('pause').addClass('play').end()
                            .each(function(){$(this).closest('.js-task-block').data('timer').stop()});
                }

                return false;
            })
            .on('click', '.js-select-responsible a', function() {
                $('[data-id="' + $(this).closest('.js-task-block').data('id') + '"]').find('.js-resp-name').text($(this).text());
                $(this).closest('.js-select-responsible').hide();
                return false;
            });

    $(window).scroll(function () {
        var scrollTop = $('html, body').scrollTop();
        if (scrollTop < 560 && scrollTop > 140) {

        } else {

        }

        if (scrollTop > 560 && !$('.js-task-input').data('inputed')) {
            var type_this = "Нарисовать логотип проекта для Синичкин";
            var index = 0;
            $('.js-task-input').data('inputed', true).val('');
            window.next_letter = function () {
                if (index <= type_this.length) {
                    $('.js-task-input:eq(0)').val(type_this.substr(0, index++)).trigger('keyup');
                    setTimeout("next_letter()", 70);
                } else {
                    var userVisible = $('.js-user-list:eq(0)').find('a:visible').eq(0).addClass('active');

                    setTimeout(function(){
                        userVisible.trigger('click');
                        setTimeout(function(){
                            $('.js-task-create:eq(0)').trigger('click');
                            setTimeout(function(){
                                $('.js-play:eq(0)').trigger('click');
                                setTimeout(function(){
                                    $('.js-play.fa-pause:eq(0)').trigger('click');
                                    setTimeout(function(){
                                        $('.js-gear:eq(0)').trigger('click');
                                        setTimeout(function(){
                                            $('.js-set-ready:eq(0)').trigger('click');
                                        }, 500)
                                    }, 1000);
                                }, 5000)
                            }, 1000)
                        }, 1000);
                    }, 1000);
                }
            };

            next_letter();
        }
    });
    $('.js-task-create').click(function () {
        var $inp = $(this).closest('.js-taskinput-block').find('.js-task-input');
        var a = $inp.val().split(' для '), text = $inp.val(), resp = 'Нет ответственного';
        if (!text) return false;

        if (a.length > 1) {
            text = a[0];
            resp = a[1].replace((new RegExp('#', 'mig')), '');
        }
        addTask(text, resp, '', Math.random());
        $inp.val('');
        return false;
    });

    $('.js-task-input').keydown(function (e) {
        var key;
        if (window.event) {
            key = window.event.keyCode;
        } else {
            key = e.keyCode;
        }
        if (key == 13) {
            $(this).closest('.js-taskinput-block').find('.js-task-create').trigger('click');
        }
    });

    function addTask(text, resp, status, id) {
        var $task = $('<div class="task-wrapper clearfix js-task-block ' + status + '" data-id="' + id + '">' +
                        '    <div class="task-title">' +
                        '        <a href="#">' + text + '</a>' +
                        '    </div>' +
                        '    <div class="task-info clearfix">' +
                        '        <div class="task-info-author"><span class="js-user-name"><a href="#" class="js-resp-name" onclick="$(this).closest(\'.js-task-block\').find(\'.js-select-responsible\').toggle();event.stopPropagation();return false;">' + resp + '</a>' +
                        '<ul class="dropdown-menu pull-right js-select-responsible"><li><a href="#">Иванов Сергей</a></li><li><a href="#">Синичкин Александр</a></li><li><a href="#">Смирнов Артем</a></li></ul></span></div>' +
                        '        <div class="task-info-timer"><a class="play"><span class="fa fa-play-circle js-play"></span></a><span class="js-timer">00:00:00</span></div>' +
                        '        <div class="task-info-control"> <span class="fa fa-close js-close-task"></span>' +
                        '            <span class="fa fa-gear js-gear">' +
                        '                <ul class="dropdown-menu pull-right js-menu" style="display: none;">' +
                        '                    <li><a href="#"><i class="fa fa-eye"></i>&nbsp;&nbsp;Наблюдаю</a></li>' +
                        '                    <li><a href="#" class="js-set-task-ready"><i class="fa fa-check-square-o"></i>&nbsp;&nbsp;<span class="js-set-ready">На проверку</span></a></li>' +
                        '                </ul>' +
                        '            </span>' +
                        '        </div>' +
                        '    </div>' +
                        '</div>'
        )
        .insertAfter($('.js-taskinput-block:eq(0)'));

        $task.data('timer', (new PM_Timer({'container': $task.find('.js-timer')})));
        $task = $task.clone()
                .insertAfter($('.js-taskinput-block:eq(1)'));
        $task.data('timer', (new PM_Timer({'container': $task.find('.js-timer')})));
    }

    var tasks = [
        {
            'text': 'Сделать выгрузку текущих бонусов в статистике по проекту в эксель',
            'resp': 'Александр Синичкин',
            'status': 'critically'
        },
        {
            'text': 'Редизайн списка рубрик подписки. Сделать стилизованные радиобаттоны и возможность добавить новую цель как сейчас, только удобнее и красивее',
            'resp': 'Евгений Васютин',
            'status': ''
        },
        {
            'text': 'Сделать страницу опций рассылки новостей клиентам',
            'resp': 'Егор Маслов',
            'status': 'ready'
        },
        {
            'text': 'Оптимизация скорости',
            'resp': 'Гоцалюк Александр',
            'status': 'not_approved'
        }
    ];

    var k, task;
    for (k in tasks) {
        task = tasks[k];
        (function (text, resp, status, id) {
            addTask(text, resp, status, id);
        })(task['text'], task['resp'], task['status'], k);
    }

    var TL_CreateTaskInput = $('.js-task-input:eq(0)'),
        TL_Tags = {
            'Responsible': 'для '
        },
        TL_HintBlocks = {
            'Responsible': $('#TL_responsible_list')
        },
        TL_HintOpened = {},
        TL_TagLen = 4,
        tag,
        TL_create_command,
        inputedText;

    TL_CreateTaskInput.keyup(function (e) {
        var key = getKeyPressed(e), t = this;
        TL_create_command = '';
        for (var keytag in TL_Tags) {
            tag = TL_Tags[keytag];

            if ($(this).val().lastIndexOf(tag) != -1 && $(this).val().lastIndexOf(tag) == ($(this).val().length - tag.length)) {
                TL_create_command = tag;
            }
        }

        if (e.ctrlKey && key == 32) { //ctrl+space
            if (TL_create_command)
                TL_ShowTaskCreateHint(this);
        } else if (e.ctrlKey && key == 78) { //ctrl+N
//            $('body,html').scrollTop(t.focus().offset().top);
            return false;
        } else if (key == 40 && TL_HintOpened.name) { //arrow down
            TL_HintOpened.container.find('li:visible').removeClass('active').eq(0).addClass('active');//.find('a').focus();
        } else if (!e.ctrlKey && key != 13) {
            TL_ShowTaskCreateHint(this);
        }
    });

    function TL_ShowTaskCreateHint(field) {
        if (!TL_create_command) return false;
        var currentTag = false;
        for (i in TL_Tags) {
            if (TL_Tags[i] == TL_create_command) {
                currentTag = i;
                break;
            }
        }
        if (currentTag) {
            TL_ShowHint(currentTag, field);
        }

        return false;
    }

    function TL_ShowHint(hintName, field) {
        if (!hintName) return false;
        var hint_block = TL_HintBlocks[hintName];

        TL_PosDivToField(hint_block, field);

        inputedText = '';

        $(field).unbind('keyup.' + hintName).bind('keyup.' + hintName, function (e) {
            var key = getKeyPressed(e);
            var lastFor = 0;
            if (lastFor = $(this).val().lastIndexOf(TL_Tags[hintName])) {
                inputedText = $(this).val().substring((lastFor + TL_Tags[hintName].length), $(this).val().length);

                var userLinks = TL_HintBlocks[hintName].find('li').show();

                if (inputedText)
                    userLinks.not(":Contains('" + inputedText + "')").hide();

                if (!userLinks.filter(":visible").get(0)) {
                    TL_HideHint()
                }
            }
        });

        TL_HintOpened = {
            'name': hintName,
            'container': hint_block
        };

        return hint_block;
    }

    function TL_HideHint() {
        if (TL_HintOpened.name) {
            TL_HintOpened.container.find('*').show().end().hide();
            TL_CreateTaskInput.unbind('keyup.' + TL_HintOpened.name);
            TL_HintOpened = {}
        }
    }

    function TL_PosDivToField(block, field_selector) {
        if (!block) return false;
        var field = $(field_selector), left = field.offset().left + (field.val().length * 5);
        block.insertAfter(field_selector);
        if (typeof(block) == 'object') {
            block.show();
        }
        return false;
    }

    function getKeyPressed(e) {
        var key;
        if (window.event) {
            key = window.event.keyCode;
        } else {
            key = e.keyCode;
        }
        return key;
    }

    function TL_CreateSelectTag(name, tag, new_val, input) {
        TL_HideHint();

        var inpval = input.val();
        var pos = inpval.lastIndexOf(TL_Tags[tag]);

        pos += TL_Tags[tag].length;
        inpval = inpval.substring(0, pos);

        input.val(
                inpval + "#" + (name == 'new' ? '' : name) + "#"
        );//.focus();

        if (name == 'new') {
            var len = input.val().length - 1;
            input.get(0).setSelectionRange(len, len);
        }

        return false;
    }

    $('.js-user-list a').click(function(){
        TL_CreateSelectTag($(this).attr('rel'), 'Responsible', false, $(this).closest('ul').prev());
        return false;
    })
});


function startTimer($block) {
    stopAllTimers()
}
function stopTimer($block) {

}
function stopAllTimers() {
    $('.js-timer-block').each(function () {
        stopTimer($(this));
    });
}