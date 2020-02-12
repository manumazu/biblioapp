$(document).ready(function() {	

	$(sliderList).each(function(i, static) {
    	var handler = [];
		$("#"+static+" li").each( function(index) {
			var val = $(this).text();
			if($.isNumeric(val))
				handler.push(val);
		});

		//$("#add_"+(i+1)).click(function(){handler.push(40);});
		$("#add_"+(i+1)).on('click', function(){
			handler.push("40");
			setSlider((i+1), handler);
		});

		setSlider((i+1), handler);
 	});



	function setSlider ( index, values ) {
		console.log(values);	
		$("#slider_"+index).slider({
		  values: values,
		  change: function( event, ui ) {
		  	console.log(ui.values);
		  }
		});
	}

});
