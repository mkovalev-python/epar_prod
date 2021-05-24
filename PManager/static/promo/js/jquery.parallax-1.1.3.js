/*
Plugin: jQuery Parallax
Version 1.1.3
Author: Ian Lunn
Twitter: @IanLunn
Author URL: http://www.ianlunn.co.uk/
Plugin URL: http://www.ianlunn.co.uk/plugins/jquery-parallax/

Dual licensed under the MIT and GPL licenses:
http://www.opensource.org/licenses/mit-license.php
http://www.gnu.org/licenses/gpl.html


(function( $ ){
	var $window = $(window);
	var windowHeight = $window.height();

	$window.resize(function () {
		windowHeight = $window.height();
	});

	$.fn.parallax = function(xpos, speedFactor, outerHeight) {
		var $this = $(this);
		var getHeight;
		var firstTop;
		var paddingTop = 0;
		
		//get the starting position of each element to have parallax applied to it		
		$this.each(function(){
		    firstTop = $this.offset().top;
		});

		if (outerHeight) {
			getHeight = function(jqo) {
				return jqo.outerHeight(true);
			};
		} else {
			getHeight = function(jqo) {
				return jqo.height();
			};
		}
			
		// setup defaults if arguments aren't specified
		if (arguments.length < 1 || xpos === null) xpos = "50%";
		if (arguments.length < 2 || speedFactor === null) speedFactor = 0.1;
		if (arguments.length < 3 || outerHeight === null) outerHeight = true;
		
		// function to be called whenever the window is scrolled or resized
		function update(){
			var pos = $window.scrollTop();				

			$this.each(function(){
				var $element = $(this);
				var top = $element.offset().top;
				var height = getHeight($element);

				// Check if totally above or totally below viewport
				if (top + height < pos || top > pos + windowHeight) {
					return;
				}

				$this.css('backgroundPosition', xpos + " " + Math.round((firstTop - pos) * speedFactor) + "px");
			});
		}		

		$window.bind('scroll', update).resize(update);
		update();
	};
})(jQuery);
*/

/*
Plugin: jQuery Parallax
Version 1.1.3
Author: Ian Lunn
Twitter: @IanLunn
Author URL: http://www.ianlunn.co.uk/
Plugin URL: http://www.ianlunn.co.uk/plugins/jquery-parallax/

Dual licensed under the MIT and GPL licenses:
http://www.opensource.org/licenses/mit-license.php
http://www.gnu.org/licenses/gpl.html


(function( jQuery ){
	var jQuerywindow = jQuery(window);
	var windowHeight = jQuerywindow.height();

	jQuerywindow.resize(function () {
		windowHeight = jQuerywindow.height();
	});

	jQuery.fn.parallax = function(xpos, speedFactor, outerHeight) {
		var jQuerythis = jQuery(this);
		var getHeight;
		var firstTop;
		var paddingTop = 0;
		
		//get the starting position of each element to have parallax applied to it		
		jQuerythis.each(function(){
		    firstTop = jQuerythis.offset().top;
		});

		if (outerHeight) {
			getHeight = function(jqo) {
				return jqo.outerHeight(true);
			};
		} else {
			getHeight = function(jqo) {
				return jqo.height();
			};
		}
			
		// setup defaults if arguments aren't specified
		if (arguments.length < 1 || xpos === null) xpos = "50%";
		if (arguments.length < 2 || speedFactor === null) speedFactor = 0.1;
		if (arguments.length < 3 || outerHeight === null) outerHeight = true;
		
		// function to be called whenever the window is scrolled or resized
		function update(){
			var pos = jQuerywindow.scrollTop();				

			jQuerythis.each(function(){
				var jQueryelement = jQuery(this);
				var top = jQueryelement.offset().top;
				var height = getHeight(jQueryelement);

				// Check if totally above or totally below viewport
				if (top + height < pos || top > pos + windowHeight) {
					return;
				}

				ypos = Math.round((top - pos) * speedFactor) > 180 ? 180 : Math.round((top - pos) * speedFactor);

				jQuerythis.css('backgroundPosition', xpos + " " + ypos + "px");
			});
		}		

		jQuerywindow.bind('scroll', update).resize(update);
		update();
	};
})(jQuery);
*/
(function (e) {
	var t = e(window);
	var n = t.height();
	t.resize(function () {
		n = t.height()
	});
	e.fn.parallax = function (r, i, s) {
		function f() {
			var s = t.scrollTop();
			o.each(function () {
				var t = e(this);
				var o = t.offset().top;
				var a = u(t);
				var f = t.attr("data-parallax");
				var l;
				if (o + a < s || o > s + n) {
					return
				}
				if (f == "element") {
					l = t.offset().top;
					t.css("top", Math.round(-1 * (l - s) * i) + "px");
				} else {
					l = t.offset().top;
					t.css("backgroundPosition", r + " " + Math.round((l - s) * i) + "px")
				}
			})
		}
		var o = e(this);
		var u;
		var a = 0;
		if (s) {
			u = function (e) {
				return e.outerHeight(true)
			}
		} else {
			u = function (e) {
				return e.height()
			}
		} if (arguments.length < 1 || r === null) r = "50%";
		if (arguments.length < 2 || i === null) i = .1;
		if (arguments.length < 3 || s === null) s = true;
		t.bind("scroll", f).resize(f);
		f()
	}
})(jQuery)