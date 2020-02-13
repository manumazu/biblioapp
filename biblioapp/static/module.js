$(document).ready(function() {	

	$(sliderList).each(function(i, static) {
    		var handler = [];
		i++;
		$("#"+static+" li").each( function(index) {
			var val = $(this).text();
			if($.isNumeric(val))
				handler.push(val);
		});

		
		$("#add_"+i).on('click', function(){
			handler.push("0");
			$("#slider_"+i).slider("destroy");
			setSlider(i, handler, static);
		});

		setSlider(i, handler, static);
 	});


	function setSlider ( index, values, static ) {
		//console.log(values);	
		$("#slider_"+index).slider({
		  min: 0,
		  max: 61,
		  values: values,
		  change: function( event, ui ) {
		  	//console.log(ui.values);
			showSliderVal(static, ui.values);
		  }
		});
	}

	function showSliderVal(static, values) {
		for(i=0;i<values.length;i++) {
			console.log(values[i]);
			if($("#"+static).length)
				$("#"+static).append('<li>'+values[i]+'<li>');
		}
	}

});
