/**
 * Created by tracker_maker on 16.11.15.
 */
function initSpecialtiesFind(addFunc, deleteFunc) {
   var $specialtyInput = $('.js-save_specialty'),
    $searchDropdown = $('.js-search_specialties'),
    $specialties = $('.js-specialties');

    var appendSkills = function (id, name) {
        var $specialty = (
            '<li class="js-skill-item">' +
            '    <div class="user-header-stat-line-progress-title clearfix">' +
            '        <div class="user-header-stat-line-progress-title-text">'+name+'' +
            '                    <a href="#" class="remove-icon js-delete_specialty" data-specialty="'+id+'"><i class="fa fa-remove"></i></a>' +
            '        </div>' +
            '        <div class="user-header-stat-line-progress-title-percent">' +
            '            ' +
            '        </div>' +
            '    </div>' +
            '    <div class="user-header-stat-line-progress-bar-2 progress">' +
            '        <div class="progress-bar blue" style="width: 0%"></div>' +
            '    </div>' +
            '</li>'
        );
        $specialties.append($specialty);
        if ($specialties.hasClass('hidden')) {
            $specialties.removeClass('hidden')
        }
    };

    $specialtyInput.keydown(function(e) {

    }).keypress(function(e) {

        var $t = $(this);
        var key = e.keyCode;
        if (key == 13) { // Enter key
            e.preventDefault();
            addFunc($t, appendSkills, $searchDropdown);
            return false;
        }
        if (key == 40) { // Down key
            $searchDropdown.find('li:visible').removeClass('active').eq(0).addClass('active').find('a').focus()
        }

    }).on('click', function(e) {e.stopPropagation();});

    $searchDropdown.keypress(function (e) {
        var key = e.keyCode;

        if (key == 40) { //down
            if ($(this).find('li.active').is(':last-child')) {
                return false
            } else {
                $(this).find('li.active').removeClass('active').next(':visible').addClass('active').find('a').focus();
            }
            return false;
        } else if (key == 38) { //up
            if ($(this).find('li.active').is(':first-child')) {
                $(this).find('li.active').removeClass('active');
                $specialtyInput.focus()
            } else {
                $(this).find('li.active').removeClass('active').prev(':visible').addClass('active').find('a').focus();
            }
            return false;
        } else if (key == 13) {
            $specialtyInput.val($(this).find('a').text()).focus();
            $searchDropdown.hide();
        }
    });

    $searchDropdown.on('click', '*', function(e) {
        e.stopPropagation();
        $specialtyInput.val($(this).text()).focus();
        $searchDropdown.hide();
        return false;
    });

    $searchDropdown.on('mouseover', 'li', (function() {
        $(this).activateListItem().find('a').blur()
    }));

    $(document).on('click', '.js-delete_specialty', function () {
        var $t = $(this);
        deleteFunc($t);
        return false;
    });

    var search_val = null;
    $specialtyInput.keyup(function() {
        var $t = $(this);
        if ($t.val() != search_val) {
            search_val = $t.val();
            if (search_val.length > 2) {
                $.post(
                    '/ajax/specialty/',
                    {
                        'action': 'specialty_search',
                        'search_text': $t.val(),
                        'user': $t.data('user-id')
                    },
                    function (response) {
                        var data = $.parseJSON(response);
                        if (data.length > 0) {
                            $searchDropdown.empty();
                            for (var i = 0; i < data.length; i++) {
                                var $skill = $('<li><a href=#>' + data[i] + '</a></li>');
                                $searchDropdown.append($skill)
                            }
                            $searchDropdown.show()
                        }
                    }
                )
            }
        }
    });

    $(document).on('click', function() {
        $searchDropdown.hide();
    });
}