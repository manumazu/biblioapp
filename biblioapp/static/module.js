$(document).ready(function() {

	var setSlider = function ( values ) {
		$("#slider").slider({
		  values: values,
		  change: function( event, ui ) {
		  	console.log(ui.values);
		  }
		});
	};
	
	var handler = [];
	$("#static li").each( function(index) {
		var val = $(this).text();
		if($.isNumeric(val))
			handler.push(val);
	});

	setSlider(handler);

});