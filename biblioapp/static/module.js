$(document).ready(function() {	

	$(sliderList).each(function(i, static) {
    	var handler = [];
    	var margin = [];
		i++;
		$("#"+static+" li").each( function(index) {
			var val = $(this).text();
			margin[i] = ((val/61)*700)+"px";
			if(i>1) {
				margin[i] = ((val/61)*700)-margin[i-1]+"px";
			}
			$(this).css({ "width" : margin[i]});
			if($.isNumeric(val))
				handler.push(val);
		});

		
		$("#add_"+i).on('click', function(){
			handler.push("0");
			$("#slider_"+i).slider("destroy");
			setSlider(i, handler);
		});

		if(!handler.length){
			handler.push("0");
		}

		setSlider(i, handler);
 	});


	function setSlider ( index, values ) {	
		//console.log(values);
		$("#slider_" + index).slider({
		  min: 0,
		  max: 61,
		  values: values,
		  change: function( event, ui ) {
		  	//console.log(ui.values);
			showSliderVal(index, ui.values);
		  },
	      /*slide: function( event, ui ) {
	        console.log( ui.value );
	      }*/
		});
	}

	function showSliderVal(index, values) {
		var margin = [];
		for(i=0;i<values.length;i++) 
		{
			var separator = $("li#sep_"+index+"_"+(i+1));
		 	margin[i] = ((values[i]/61)*700);
			if(i>0) {
				margin[i] = (((values[i]/61)*700)-(margin[i-1]))+30;
				console.log(margin[i]);
			}
			if(separator.length) { //update existing value
				separator.text(values[i]);
				separator.css({ "width" : margin[i]+'px'});
			}
			else { //add new separator // style="padding-left:'+ margin +'"
				//console.log(margin);
				$("#static_" + index).append('<li id="sep_'+ index +'_'+ (i+1) +'">'+ values[i] +'</li>');
			}
		}
	}

	$("#saveModule").on('click', function() {
	 //'/module/<app_id>'
	 	var lines = new Object();
		$(sliderList).each(function(i, static) {
			var handler = [];
			i++;
			$("#"+static+" li").each( function(index) {
				var val = $(this).text();
				if($.isNumeric(val))
					handler.push(val);
			});
			if(handler.length) {
				lines[i] = handler;
			}
	 	});

	 	var elements = JSON.stringify(lines);

		$.ajax({
			dataType: 'json',
        	contentType: 'application/json',
			data: elements,
		    type: 'POST',
		    url: $("#formEditArduino").attr('action')
		});
	});

});
