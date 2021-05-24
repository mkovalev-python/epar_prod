/**
 * Created with PyCharm.
 * User: Gvammer
 * Date: 20.02.14
 * Time: 18:44
 */
var sitePanel = function(params){
    this.pos = params.pos;
    this.blocks = {};
    this.$element = $('<div class="navbar-collapse"><i class="fa fa-times js-bottom-panel-close"></i></div>').append('<ul class="nav navbar-nav js-p_container"></ul>');
    this.$element = $('<div class="navbar-inverse"></div>').addClass(this.pos).addClass('bt-panel').append(this.$element);
    this.handlers = {};
    this.$container = this.$element.find('.js-p_container');
    this.init();
};

sitePanel.prototype = {
    'init': function() {
        var t = this;
        this.$element
            .find('.js-bottom-panel-close')
                .click(function(){
                    t.hide();
                }).end()
            .appendTo('body');

        this.toggle();
    },
    'addCloseHandler': function(name, func) {
        if (!this.handlers[name]) {
            this.$element
            .find('.js-bottom-panel-close')
            .click(func);
            this.handlers[name] = func;
        }
        return this;
    },
    'addBlock': function(name, $element) {
        if (!(name in this.blocks)){
            this.blocks[name] = $element;
            this.$container.append($('<li></li>').append($element));
        }
        this.toggle();
    },
    'removeBlock': function(name) {
        if (name in this.blocks){
            this.blocks[name].parent().remove();
            delete this.blocks[name];
        }
        this.toggle();
    },
    'toggle': function() {
        for (var i in this.blocks) {}

        if (i) {
            this.show();
        } else {
            this.hide();
        }
    },
    'show': function() {
        this.$element.show();
    },
    'hide': function() {
        this.$element.hide();
    }
};
var bottomPanel = false;
$(function(){
    bottomPanel = new sitePanel({
        'pos':'bottom'
    })
});