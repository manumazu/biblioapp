$(document).ready(function() {	

	$(sliderList).each(function(i, static) {
		console.log(static);

    	var handler = [];
    	var margin = [];
		i++;
		$("#"+static+" li").each( function(index) {
			var val = $(this).text();
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


	function setSlider ( index, values) {	
		//console.log(values);
		$("#slider_" + index).slider({
		  min: 0,
		  max: 61,
		  values: values,
	      create: function (event, ui) {
	        $.each( values, function(i, v){
	            updateValue({
	                value: v,
	                handle: $('#slider_'+index+' .ui-slider-handle').eq(i) 
	            });
	        });
	      },		  
	      slide: function (event, ui) {
	        updateValue(ui);
	      }
		});
	}	

	function showSliderVal(index, values, posLeft) 
	{
		for(i=0;i<values.length;i++) 
		{
			var separator = $("li#sep_"+index+"_"+(i+1));
			if(separator.length) { //update existing value
				separator.text(values[i]);
			}
			else { //add new separator // style="padding-left:'+ margin +'"
				//console.log(margin);
				$("#static_" + index).append('<li id="sep_'+ index +'_'+ (i+1) +'">'+ values[i] +'</li>');
			}
			separator.css({ "width" : posLeft+"px", "text-align" : "right"});			
			//computeListWidth(separator,values)
			//if(i>0) {
			/*	for (var j = 1; j <= values.length ; j++) {
					console.log(j);
					margin[i] = ((values[i]/61)*700)-margin[i-j]+30;
					//separator.css({ "width" : margin[i]+"px"});
					console.log(i-j);
				}
			//}*/
		}
	}

	function updateValue (ui) {
	    $(ui.handle).attr('data-value', ui.value);
	};

	$("#saveStaticPositions").on('click', function() {
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
	 	//console.log(elements);

		$.ajax({
			dataType: 'json',
        	contentType: 'application/json',
			data: elements,
		    type: 'POST',
		    url: $("#formEditArduino").attr('action')
		});
	});

	$('#colorEditor-save').on('click', function() {
		var c = getColor();
		$('input[name="mood_color"]').val(c);
		$('#rgbText').text("RGB code update");
	});

});
