$(document).ready(function(){
					$(function() {
					  $('.slider').bxSlider({
					    pager:false,
						auto:true,
						controls:false,
						pause:4000,
						mode: "fade"
					  });
					  $('#head_slider').bxSlider({
					    pager:false,
						auto:true,
						controls:false,
						pause:8000,
						speed:1500,
						mode: "horizontal"
					  });
					});
					
});