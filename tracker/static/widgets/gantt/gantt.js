/**
 * Created with PyCharm.
 * User: Gvammer
 * Date: 27.07.14
 * Time: 17:22
 */
$.fn.getLeft = function(){
    var left =  this.css('left').replace('px', '') * 1;
    if (left < 0) left = 0;
    return left;
}

if(!Date.prototype.toLocaleFormat){
    Date.prototype.toLocaleFormat = function(format) {
        var f = {
            Y : this.getFullYear(),
            y : this.getFullYear()-(this.getFullYear()>=2e3?2e3:1900),
            m : this.getMonth() + 1,
            d : this.getDate(),
            H : this.getHours(),
            M : this.getMinutes(),
            S : this.getSeconds()
        }, k;
        for(k in f)
            format = format.replace('%' + k, f[k] < 10 ? "0" + f[k] : f[k]);
        return format;
    }
}

var GANTT = function (options, events, milestones) {
    this.from = options.from; //timestamp
    this.to = options.to; //timestamp
    this.now = new Date();
    this.monthNames = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];
    this.pxRatio = 0;

    this.container = options.container;
    this.DAY_IN_MILLISECONDS = 86400000;
    this.visibleSpan = this.DAY_IN_MILLISECONDS * 11;//2592000000;
    this.eventObjects = {};
    this.timelinePadding = 86400000 * 4;
    this.eventHeight = 25;
    this.eventMargin = 2;
    this.dateLabelHeight = 25;
    this.topMargin = 0;
    this.subLabel = 'month';
    this.markToday = 'line';
    this.minHeight = 600;
    this.milestones = milestones;
    this.events = events;
    this.events.sort(this.sortEventsFunc);
    var t = this;

    this.nowTime = this.stripTime(new Date());
    this.init();
    this.scrollToStart();
    setTimeout(function () {
        t.thumbnail = new cTimeThumb({
            container: $('div.diagramma').get(0),
            scrollWin: $('.scroll-bar').show().get(0),
            big: t
        });
    }, 1000);
};

GANTT.prototype = {
    init: function () {
        this.initDates();

        this.initContainers();
        this.initSize();

        this.initEvents();

        this.drawEvents();
        this.drawResponsibles();
        this.drawDates(0);
        this.drawMilestones();
        this.initWebEvents();
    },
    redraw: function (callback) {
        this.container.empty();
        this.$datesTopContainer.empty();
        this.initContainers();
        this.initSize();
        this.drawEvents(callback);
        this.drawResponsibles();
        this.drawDates(0);
        this.drawMilestones();
        this.initWebEvents();
    },

    goToToday: function () {
        this.goToDate(this.today, 0);
    },

    getLeftTime: function () {
        return Math.floor(this.startTime - this.getLeftPx() / this.pxRatio);
    },

    getRightTime: function () {
        return Math.floor(this.startTime - (this.getLeftPx() - this.visibleWidth) / this.pxRatio);
    },

    getLeftPx: function () {
        return -this.container.scrollLeft();
    },

    goToPx: function (x) {
        this.container.scrollLeft(-x);
    },

    'initDates': function () {
        var t = this;
        // need to convert dates to UTC
        for (var i = 0; i < this.events.length; i++) {
            for (var j = 0; j < this.events[i].dates.length; j++) {
                this.events[i].dates[j] = this.stripTime(this.events[i].dates[j]);
            }
        }

        // CALCULATING MORE THINGS
        // generating relevant dates
        t.today = t.stripTime(new Date(Date.now()));

        if (t.defaultStartDate == null) {
            t.defaultStartDate = t.today;
        }

        if (t.startDate == null) {
            if (t.events.length > 0) {
                t.startDate = t.events[0].dates[0];
                for (var i = 1; i < t.events.length; i++)
                    if (t.events[i].dates[0] < t.startDate)
                        t.startDate = t.events[i].dates[0];
            } else {
                return;
            }
        }

        t.startDate = t.stripTime(t.startDate);

        if (t.startDate > t.defaultStartDate)
            t.startDate = t.defaultStartDate;
        t.startDate = new Date(t.startDate.getTime() - t.timelinePadding);
        t.startTime = t.startDate.getTime();

        if (t.endDate == null) {
            if (t.events.length > 0) {
                t.endDate = this.getEndDate(t.events[0].dates);
                for (var i = 0; i < t.events.length; i++)
                    if (this.getEndDate(t.events[i].dates) > t.endDate)
                        t.endDate = t.getEndDate(t.events[i].dates);
            }

            if (t.milestones) {
                if (t.milestones.length > 0) {
                    for (var i = 0; i < t.milestones.length; i++)
                        if (t.milestones[i].date > t.endDate)
                            t.endDate = t.milestones[i].date;
                }
            }
        }



        if (t.endDate < t.defaultStartDate)
            t.endDate = t.defaultStartDate;

        t.endDate = this.stripTime(new Date(Math.max(t.endDate.getTime() + t.DAY_IN_MILLISECONDS, t.startDate.getTime() + t.visibleSpan) + t.timelinePadding))

    },
    'initContainers': function () {
        var t = this;
        t.$datesTopContainer = $('.gantt-dates-top');
        t.$detailEventWin = $('.js-event-detail');
        t.$desk = $('<table></table>', {
            'class': 'gantt-event-desk'
        }).appendTo(t.container);

        t.$datesTop = $('<table class="gantt-dates-container">' +
            '<tr><td><div class="gantt-top-sub-dates"></div></td></tr>' +
            '<tr><td><div class="gantt-top-dates stars"></div></td></tr>' +
            '</table>').appendTo(t.$datesTopContainer);

        t.$datesTop.on('touchstart mousedown', function (e, e2) {
            if (e.type === 'touchstart') {
                if (e2) {
                    e2 = e2.originalEvent.touches[0] || e2.originalEvent.changedTouches[0];
                } else {
                    e = e.originalEvent.touches[0] || e.originalEvent.changedTouches[0];
                }
            }
            var clientX = e.clientX || e2.clientX;
            $(this).data('scrolling', true);
            $(this).data('scroll', $(this).parent().scrollLeft());
            $(this).data('x', clientX);
        });

        t.$desk.on('touchstart mousedown', function(e){
            if (e.type === 'touchstart') {
                t.$datesTop.trigger('touchstart', e);
            } else {
                t.$datesTop.trigger('mousedown', e);
            }
            e.stopPropagation();
            return false;
        });

        $(document)
            .unbind('mouseup.gantt touchend.gantt').bind('mouseup.gantt touchend.gantt', function () {
                t.$datesTop.data('scrolling', false);
            })
            .unbind('mousemove.gantt touchmove.gantt').bind('mousemove.gantt touchmove.gantt', function (e) {
                if (e.type === 'touchmove') {
                    e = e.originalEvent.touches[0] || e.originalEvent.changedTouches[0];
                }
                if (t.$datesTop.data('scrolling')) {
                    t.$datesTop.parent().scrollLeft(
                        t.$datesTop.data('scroll') + t.$datesTop.data('x') - e.clientX
                    );
                    t.thumbnail.synchronize();
                }
            });
    },
    'initSize': function () {
        var t = this;
        // this ratio converts a time into a px position
        // t.visibleWidth = t.domElement.clientWidth;
        t.visibleWidth = $(t.container).width();

        t.pxRatio = t.visibleWidth / t.visibleSpan;

//        if (!t.totalWidth) //if not redraw (for zoom, for example)
        t.totalWidth = t.pxRatio * (t.endDate.getTime() - t.startDate.getTime());

        t.maxLeftPx = t.totalWidth - t.visibleWidth;

        // SPLIT THE DATES INTO THE ROW THAT THEY BELONG TO
        // TODO
        // this is a greedy algo that definitely isn't optimal
        // it at least needs to find the latest row that still fits
        // this, however, may cause very strange behavior (everything being on the 2nd line),
        // so I'm going to prefer this in the short term

        // calculated here so it can be used in splitting dates
        t.circleRadius = t.eventHeight / 2;
    },
    'initEvents': function () {
        var t = this;
        t.eventRows = [
            {
                'id': 0,
                'events': []
            }
        ];
        t.rowLastPxs = [0];

        for (var i = 0; i < t.events.length; i++) {
            var found = false;
            var startPx = t.msToPx(t.events[i].dates[0].getTime()) - t.circleRadius;
            for (var j = 0; j < t.eventRows.length; j++) {
                var currentRow = t.eventRows[j];

                if (currentRow.responsible && currentRow.responsible != t.events[i].responsible) continue;
                //t.rowLastPxs[j] < startPx
                if (t.canIAddEventToRow(t.events[i], currentRow) && (
                    !currentRow.responsible ||
                        currentRow.responsible == t.events[i].responsible)
                    ) {

                    if (!t.eventRows[j].events) t.eventRows[j].events = [];
                    t.eventRows[j].events.push(t.events[i]);
                    if (!currentRow.responsible) {
                        if (t.events[i].responsible)
                            currentRow.responsible = t.events[i].responsible;
                        else
                            currentRow.responsible = 'null';
                    }
                    t.rowLastPxs[j] = t.msToPx(this.getEndDate(t.events[i].dates).getTime())/* + t.circleRadius*/;
                    found = true;
                    break;
                }
            }
            if (!found) {
                var newRow = {
                    'id': t.eventRows.length,
                    'events': [t.events[i]]
                };
                if (t.events[i].responsible)
                    newRow.responsible = t.events[i].responsible;
                else
                    newRow.responsible = 'null';

                t.eventRows.push(newRow);

                t.rowLastPxs.push(t.msToPx(t.getEndDate(t.events[i].dates).getTime())/* + t.circleRadius*/);
            }
        }
        t.eventRows.sort(t.sortRowsFunc);
        // a few more calculations and creation

        t.eventsHeight = t.eventRows.length * (t.eventMargin * 2 + t.eventHeight);

        t.totalHeight = t.dateLabelHeight + t.eventsHeight + t.topMargin;
        if (t.totalHeight < t.minHeight) {
            t.totalHeight = t.minHeight;
        }
    },
    'drawEvents': function (callback) {
        var t = this;

        t.$desk.css({
            'width': t.totalWidth
        });
//        t.$desk.parent().css({
//            'height': t.minHeight
//        });
        t.$datesTop.css('width', t.totalWidth);

        // drawing events
        var lastResp, currentRow;
        t.arRespId = [];
        t.arResponsibles = {};

        for (var row = 0; row < t.eventRows.length; row++) {
            currentRow = t.eventRows[row];
            currentRow.$container = $('<tr><td><div></div></td></tr>').attr(
                'id', 'row_' + row + '_' + currentRow.responsible
            ).appendTo(t.$desk).find('div').data(
                    'responsible',
                    currentRow.responsible
                );
            if (lastResp != currentRow.responsible) {
                currentRow.$container.addClass('top-row');
            }

            t.arRespId.push(currentRow.responsible);

            for (var col = 0; col < currentRow.events.length; col++) {
                var event = currentRow.events[col];

                var startX = (event.dates[0].getTime() - t.startTime) * t.pxRatio;

                var $elem = (new EventBlock(event)).$elem;

                if (event.responsible)
                    t.arResponsibles[event.responsible] = AR_USERS[event.responsible];

                if (event.dates.length == 1) {  // it's a single point
                    $elem.css('width', t.circleRadius - 2);
                } else {  // it's a range
                    var width = (t.getEndDate(event.dates) - event.dates[0]) * t.pxRatio;
                    if (width <= 0) continue;
                    // left rounded corner
                    $elem.css('width', width - 2);
                }

                $elem.css({
                    'left': startX,
                    'margin': t.eventMargin,
                    'top': t.eventMargin
                });

                currentRow.$container.append($elem);

                t.eventObjects[event.id] = $elem;

                if (typeof event.attrs != "undefined") {
                    $elem.attr(event.attrs);
                }

                $elem.addClass('chronoline-event');
            }
            lastResp = currentRow.responsible;
        }
        this.dateLineY = t.totalHeight - t.dateLabelHeight;
        if (callback) callback();
    },
    'canIAddEventToRow': function (event, row) {
        var t = this,
            eventStartDate = event.dates[0],
            eventEndDate = event.dates[1];

        if (!row.events) return true;
        var l = row.events.length;
        for (var i = 0; i < l; i++) {
            var e = row.events[i];
            var ds = new Date(e.dates[0].getTime());
            var de = new Date(e.dates[1].getTime());
            ds.setHours(e.dates[0].getHours() - 2);
            de.setHours(e.dates[1].getHours() + 2);
            if (ds < eventEndDate && de > eventStartDate) {
                return false;
            }
        }

        return true;
    },
    'drawResponsibles': function () {
        var resp, lastRespId;
        var $respTable = $('<div></div>').addClass('gantt-reponsibles');
        for (var i = 0; i < this.arRespId.length; i++) {
            resp = this.arResponsibles[this.arRespId[i]];
            var $respTr = $('<div class="gantt-responsibles-row"><div class="gantt-resp-block"></div></div>')
                .appendTo($respTable).find('div');
            if (resp && this.arRespId[i] != lastRespId) {
                $respTr.
                    append('<a href="/user_detail/?id=' + this.arRespId[i] + '" class="gantt-resp-name">' + resp + '</a>');
//                    append('<img class="gant-resp-avatar" src="/static/images/avatar_unknown.png" />');


                $respTr.addClass('top-row');
            } else if (!resp && lastRespId != 'null') {
                $respTr.text('Нет');

                $respTr.addClass('top-row');
            }
            lastRespId = this.arRespId[i];
        }
        this.container.prepend($respTable);
        if ($respTable.height() < this.minHeight) {
            $respTable.css({
                'height': this.minHeight - this.dateLabelHeight
            })
        }
    },
    'drawDates': function (leftPxPos) {
        this.$dateContainer = this.$datesTop.find('.gantt-top-dates');
        this.$dateSubContainer = this.$datesTop.find('.gantt-top-sub-dates');

        var t = this;
        var newStartPx = Math.max(0, leftPxPos - t.visibleWidth + 7);
        var newEndPx = Math.min(t.totalWidth, leftPxPos + 2 * t.visibleWidth);

        var newStartDate = new Date(t.pxToMs(newStartPx));
        newStartDate = new Date(Date.UTC(newStartDate.getUTCFullYear(), newStartDate.getUTCMonth(), 1));

        var newStartMs = newStartDate.getTime();
        var newEndDate = t.stripTime(new Date(t.pxToMs(Math.min(t.totalWidth, leftPxPos + 2 * t.visibleWidth))));
        newEndDate = new Date(Date.UTC(newEndDate.getUTCFullYear(), newEndDate.getUTCMonth(), newEndDate.getUTCDate()));

        var newEndMs = newEndDate.getTime();

        if (t.visibleSpan > 30 * t.DAY_IN_MILLISECONDS)
            t.hashInterval = function(date) {
                return date.getDay() == 1;
            }


        if (t.drawnStartMs == null) {  // first time
            t.drawnStartMs = newStartMs;
            t.drawnEndMs = newEndMs;
            t.drawLabelsHelper(newStartMs, newEndMs);
        } else if (newStartMs > t.drawnEndMs) {  // new labels are to the right
            t.drawLabelsHelper(t.drawnEndMs, newEndMs);
            t.drawnEndMs = newEndMs;
        } else if (newEndMs < t.drawnStartMs) {  // to the left
            t.drawLabelsHelper(newStartMs, t.drawnStartMs);
            t.drawnStartMs = newStartMs;
        } else {  // overlap
            if (newStartMs < t.drawnStartMs) {
                t.drawLabelsHelper(newStartMs, t.drawnStartMs);
                t.drawnStartMs = newStartMs;
            }
            if (newEndMs > t.drawnEndMs) {
                t.drawLabelsHelper(t.drawnEndMs, newEndMs);
                t.drawnEndMs = newEndMs;
            }
        }
    },
    drawMilestones: function () {
        var t = this;
        var l = t.milestones.length;
        for (var i = 0; i < l; i++) {
            var milestone = t.milestones[i];
            var left = t.msToPx(milestone.date.getTime());

            var $milestone = $('<a></a>', {
                'class': 'fa fa-star',
                'href': '#',
                'title': milestone.name
            });
            $milestone.data('id', milestone.id);
            if (milestone.tasksId)
                $milestone.data('tasks', milestone.tasksId.join('|'));

            $milestone.appendTo(t.$dateContainer);
            $milestone.css('left', left);
            $milestone.css({
                'position': 'absolute'
            });
            if (milestone.closed) {
                $milestone.addClass('green');
            } else {
                $milestone.addClass('red');
            }

            //highlight milestone and it tasks
            $milestone.click(function(){
                $(this).toggleClass('highlighted');
                $('.milestone-mini[data-id='+$(this).data('id')+']').toggleClass('highlighted');
                var aTasksId = $(this).data('tasks'), taskId;
                if (aTasksId) {
                    aTasksId = aTasksId.split('|');
                    for (var i in aTasksId) {
                        taskId = aTasksId[i];
                        t.getEventNode(taskId).toggleClass('highlighted');
                    }
                }
                return false;
            });
        }
        return this;
    },
    'getEvent': function(id) {
        var t = this;
        var l = t.events.length;
        for (var i = 0; i < l; i++) {
            if (t.events[i].id == id) {
                return t.events[i];
            }
        }
        return null;
    },

    'getEventNode': function(id) {
        return $('.gantt-event[data-id='+id+']');
    },
    'addEvent': function (event) {
        if (!event || !event.id) {
            return false;
        }
        var t = this;
        if (t.getEvent(event.id)) {
            return false;
        }

        var bRowMatch, bRowWasFound;
        for (i = 0; i < t.eventRows.length; i++) {
            var row = t.eventRows[i];
            if (event.responsible) {
                if (event.responsible == row.responsible) {
                    bRowMatch = true;
                }
            } else {
                if (row.responsible == 'null') {
                    bRowMatch = true;
                }
            }
            if (bRowWasFound && !bRowMatch) {
                var $rowToPrepend = row.$container.closest('tr');
                var $newRow = $('<tr><td><div></div></td></tr>').insertBefore($rowToPrepend);
                var newRow = {
                    'id': t.eventRows.length,
                    'events': [],
                    '$container': $newRow
                }
                var l = t.eventRows.length;
                for (var k = l - 1; k >= i; k--) {
                    t.eventRows[k + 1] = t.eventRows[k];
                }
                t.eventRows[i] = newRow;
                row = newRow;
            }

            if (bRowMatch && t.canIAddEventToRow(event, row)) {
                t.events.push(event);
                t.insertEventToRow(event, row);
                break;
            }

            bRowWasFound = bRowMatch;
        }
        return true;
    },
    'insertEventToRow': function(event, row) {
        var t = this;
        var startX = (event.dates[0].getTime() - t.startTime) * t.pxRatio;

        var eventBlock = new EventBlock(event);

        if (event.dates.length == 1) {  // it's a single point
            eventBlock.$elem.css('width', t.circleRadius - 2);
        } else {  // it's a range
            var width = (t.getEndDate(event.dates) - event.dates[0]) * t.pxRatio;
            if (width <= 0) return;
            // left rounded corner
            eventBlock.$elem.css('width', width - 2);
        }
        eventBlock.$elem.appendTo(row.$container).css({
            'left': startX,
            'margin': t.eventMargin
        });

        row.events.push(event);
    },
    'scrollToStart': function () {
        var maxScrollLeft = this.container.get(0).scrollWidth - this.container.get(0).clientWidth;
        var nowScrollLeft = this.msToPx(this.nowTime) - (this.container.get(0).clientWidth / 2);
        this.container.scrollLeft(
            maxScrollLeft < nowScrollLeft ? maxScrollLeft : nowScrollLeft
        );
    },
    'isHoliday': function(date){
        return date.getDay() == 0 || date.getDay() == 6;
    },
    'drawLabelsHelper': function (startMs, endMs) {
        var t = this;
        var month = '';
        var prevMs = false;
        var hourLength = t.DAY_IN_MILLISECONDS / 24;

        for (var curMs = startMs; curMs < endMs; curMs += t.DAY_IN_MILLISECONDS) {
            if (prevMs && t.visibleSpan < t.DAY_IN_MILLISECONDS * 4) {
                for (var curMsHour = prevMs + hourLength; curMsHour < curMs; curMsHour += t.DAY_IN_MILLISECONDS / 24) {
                    var xH = t.msToPx(curMsHour);
                    $('<div></div>').css({
                        'position': 'absolute',
                        'height': t.dateLineY,
                        'background-color': 'black',
                        'width': '1px',
                        'left': xH
                    }).appendTo(t.container).addClass('gantt-label');
                }
            }
            var curDate = new Date(curMs);
            var day = curDate.getUTCDate();
            var x = t.msToPx(curMs);

            // the little hashes
            if (t.hashInterval == null || t.hashInterval(curDate) || t.isHoliday(curDate)) {
                $line = $('<div></div>').css({
                    'position': 'absolute',
                    'height': (t.dateLineY + 5),
                    'top': 0,
                    'left': x
                }).appendTo(this.container).addClass('gantt-label');
                if (t.isHoliday(curDate)) {
                    $line.addClass('holyday-line').css('width', (t.DAY_IN_MILLISECONDS * t.pxRatio) + 'px');
                } else {
                    $line.addClass('day-line');
                }
            }

            if (t.hashInterval == null || t.hashInterval(curDate)) {
                // the labels directly below the hashes
                if (t.labelInterval == null || t.labelInterval(curDate)) {
                    var displayDate = String(day);
                    if (displayDate.length == 1)
                        displayDate = '0' + displayDate;
                    var $date = $('<span>' + displayDate + '</span>').css({
                        'position': 'absolute',
                        'left': x,
                        'top': 0
                    }).appendTo(t.$dateContainer).addClass('gantt-label').addClass('day');
                }
            }



            // sublabels. These can float
            var monthNow = t.formatDate(curDate, '%b').toUpperCase();

            if (day == 1 && t.subLabel == 'month' && month != monthNow) {
                month = monthNow;
                var $subLabel = $('<span>' + monthNow + '</span>').css({
                    'position': 'absolute',
                    'left': x
                }).appendTo(t.$dateSubContainer).addClass('gantt-label').addClass('month');


                if (t.floatingSubLabels) {
                    // bounds determine how far things can float
                    $subLabel.css('left', x);

                    var endOfMonth = new Date(Date.UTC(curDate.getUTCFullYear(), curDate.getUTCMonth() + 1, 0));
                    $subLabel.css('right',
                        Math.min((endOfMonth.getTime() - t.startTime) * t.pxRatio - 5,
                            t.totalWidth));
                    t.floatingSet.push($subLabel);
                }
            }
            prevMs = curMs;
        }

        // special markers for now
        if (t.markToday && (curMs = t.today.getTime())) {
            var x = t.msToPx(curMs);
            if (t.markToday == 'labelBox') {
                label.attr({'text': label.attr('text') + '\n' + t.formatDate(curDate, '%b').toUpperCase(),
                    'font-size': t.fontAttrs['font-size'] + 2,
                    'y': t.bottomHashY + t.fontAttrs['font-size'] + 5});
                var bbox = label.getBBox();
                var labelBox = t.paper.rect(bbox.x - 2, bbox.y - 2, bbox.width + 4, bbox.height + 4);
                labelBox.attr('fill', '90-#f4f4f4-#e8e8e8');
                labelBox.insertBefore(label);
            } else if (t.markToday == 'line') {
                var $line = $('<div></div>').css({
                    'position': 'absolute',
                    'height': (t.dateLineY),
                    'top': 0,
                    'left': x
                }).appendTo(this.container).addClass('gantt-label');

                $line.addClass('today-line');
            }
            var $now = $('<span>Сегодня</span>').css({
                'position': 'absolute',
                'left': x,
                'top': 0
            }).appendTo(t.$dateSubContainer).addClass('gantt-label').addClass('today-label');
        }
    },
    'formatDate': function (date, formatString) {
        var t = this;
        // done in the style of c's strftime
        // TODO slowly adding in new parts to this
        // note that this also doesn't escape things properly. sorry
        var ret = formatString;
        if (formatString.indexOf('%d') != -1) {
            var dateNum = date.getUTCDate().toString();
            if (dateNum.length < 2)
                dateNum = '0' + dateNum;
            ret = ret.replace('%d', dateNum);
        }
        if (formatString.indexOf('%b') != -1) {
            var month = t.monthNames[date.getUTCMonth()];//.substring(0, 3);
            ret = ret.replace('%b', month);
        }
        if (formatString.indexOf('%Y') != -1) {
            ret = ret.replace('%Y', date.getUTCFullYear());
        }

        return ret;
    },
    'initWebEvents': function () {
        var t = this;
        t.$detailEventWin.find('.js-close').click(function () {
            t.$detailEventWin.hide();
            return false;
        }).end().find('.js-send-message').click(function () {
                var b = this,
                    $comment = t.$detailEventWin.find('.js-comment'),
                    id = t.$detailEventWin.find('.js-event-id').val(),
                    model = $('.gantt-event[data-id=' + id + ']').data('model');
                $(b).pushTheButton();
                PM_AjaxPost(
                    '/task_handler',
                    {
                        'task_id': id,
                        'task_message': $comment.val()
                    },
                    function (data) {
                        $comment.val('');
                        $(b).pullTheButton();
                        model.set('last_message', {
                            'author': data['author']['last_name'] + ' ' + data['author']['name'],
                            'text': data['text'],
                            'date': data['date']
                        });
                        t.renderDetailWindow(model);
                    },
                    'json'
                )
                return false;
            });

        $('.gantt-dates-top').scroll(function () {
            t.container.scrollLeft(
                $(this).scrollLeft()
            )
        });

        $('.gantt-event').mousedown(function(e) {
            e.stopPropagation();
            e.preventDefault();
            return false;
        });

        t.container.on('mouseover', '.gantt-event > a', function (e) {
                $(this).css('width', '100%');
                var $t = $(this).parent();
                if (!$t.data('width')) {
                    $t.data('width', $t.css('width'));
                    $t.data('zi', $t.css('z-index'));
                }

                if (parseInt($t.css('width')) < 100) {
                    $t.css('width', 200);
                }


                $t.addClass('activated');
                $t.css('z-index', '999');
            })
            .on('mouseout', '.gantt-event', function () {
                $(this).children('a').css('width', 'auto');
                var $t = $(this);
                $t.removeClass('activated');
                $t.css('width', $t.data('width'));
                $t.css('z-index', $t.data('zi'));
                $t.data('width', false);
            })
            .on('click', '.gantt-event > a', function () {
                var $event = $(this).closest('.gantt-event');
                var model = new window.taskClass({
                    'id': $event.data('id')
                });
                model.getFromServer(function () {
                    t.renderDetailWindow(model);
                    $event.data('model', model);
                });

                return false;
            });

        this.container.scroll(function () {
            var sc = this;
            $(this).find('.gantt-reponsibles').css(
                'left',
                $(this).scrollLeft()-1
            );
            $('.gantt-dates-top').scrollLeft(
                $(this).scrollLeft()
            );
            if (t.drawDatesScrollTimeout) {
                clearTimeout(t.drawDatesScrollTimeout);
            }
            t.drawDatesScrollTimeout = setTimeout(function () {
                t.drawDates($(sc).scrollLeft());
//                if (t.newEventsAjax) t.newEventsAjax.abort();
                var dateFrom = new Date(t.pxToMs($(sc).scrollLeft()));
                var dateTo = new Date(t.pxToMs($(sc).scrollLeft() + t.visibleWidth));
                t.newEventsAjax = $.post('/task_handler', {
                        'action': 'ganttAjax',
                        'date_create[]': [
                            dateFrom.toLocaleFormat("%d.%m.%Y"),
                            dateTo.toLocaleFormat("%d.%m.%Y")
                        ],
                        'project': window.currentProject ? window.currentProject : 0
                    }, function (data) {
                        for (var i in data.tasks) {
                            var task = data.tasks[i];
                            var dateStart = new Date(task.dateCreateGantt);
                            var dateEnd = new Date(task.endTime);
                            task.dates = [
                                dateStart, dateEnd
                            ];

                            task.project = task.project__name;
                            task.status = task.status__code;
                            t.addEvent(task);
                        }
                    },
                    'json')
            }, 300);
        });
    },
    'renderDetailWindow': function (model) {
        var t = this;
        var resp = {};
        if (model.get('responsible'))
            resp = model.get('responsible')[0];

        console.log(model);

        t.$detailEventWin
            .find('.js-event-id')
            .val(model.id).end()
            .find('.js-e-d-title')
            .text(model.get('name')).attr('href', model.get('url')).end()
            .find('.js-e-d-date-create')
            .text(model.get('dateCreate')).end()
            .find('.js-e-d-author')
            .text(
                model.get('author') ? model.get('author')['last_name'] + ' ' + model.get('author')['first_name'] : ''
            );


        if (resp)
            t.$detailEventWin.find('.js-e-d-resp')
            .text(resp['name']).attr('href', '/user_detail/?id=' + resp['id']);

        var $detailText = t.$detailEventWin.find('.js-e-d-desc');
        if (model.get('text')) {
            $detailText.text(model.get('text')).show();
        } else {
            $detailText.hide();
        }
        var $lastMes = t.$detailEventWin.find('.js-e-d-last-mes');
        if (model.get('last_message')) {
            var m = model.get('last_message');
            $lastMes.find('.js-e-d-last-mes-author').text(m['author']).end()
                .find('.js-e-d-last-mes-date').text(m['date']).end()
                .find('.js-e-d-last-mes-text').text(m['text']).end()
                .show();
        } else {
            $lastMes.hide();
        }
        t.$detailEventWin.show().css('height', $(window).height());
    },
    'assignEventTo': function(eventId, respId) {
        var t = this;
        var event = t.getEvent(eventId), currentRow;
        if (event) {
            event.responsible = respId;
            for (var row = 0; row < t.eventRows.length; row++) {
                currentRow = t.eventRows[row];

                if (currentRow.responsible != respId) {
                    continue;
                }
                if (t.canIAddEventToRow(event, currentRow)) {
                    t.insertEventToRow(event, currentRow);
                    return true;
                }
            }
        }
        return null;
    },
    'sortRowsFunc': function (a, b) {
        if (a.responsible == b.responsible) return 0;
        if (a.responsible == 'null') return 9999;
        if (b.responsible == 'null') return -9999;

        a = parseInt(a.responsible);
        b = parseInt(b.responsible);

        return a - b;
    },
    'sortEventsFunc': function (a, b) {
        var a = a.dates,
            b = b.dates,
            ar, br;

        ar = parseInt(a.responsible);
        br = parseInt(b.responsible);
        if (ar != br) {
            return ar > br ? 1 : -1;
        } else {
            var aEnd = a[a.length - 1].getTime();
            var bEnd = b[b.length - 1].getTime();
            if (aEnd != bEnd) {
                return aEnd - bEnd;
            }
            return a[0].getTime() - b[0].getTime();
        }
    },
    'pxToMs': function (px) {
        return this.startTime + px / this.pxRatio;
    },
    'msToPx': function (ms) {
        return (ms - this.startTime) * this.pxRatio;
    },
    'getEndDate': function (dateArray) {
        return dateArray[dateArray.length - 1];
    },
    'stripTime': function (date) {
        return new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate(), date.getHours(), date.getMinutes(), date.getSeconds()));
    }
};