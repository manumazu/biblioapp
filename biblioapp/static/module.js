$(document).ready(function() {

	$('#alertPreview').hide();	
	$('#alertSave').hide();

	$(sliderList).each(function(i, static) {
		//console.log(static);

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
		  max: parseInt(nb_cols)-1,
		  values: values,
		  change: function( event, ui ) {
			updatePositionValues(index, ui.values);	
		  },
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

	function updatePositionValues(index, values) 
	{
		for(i=0;i<values.length;i++) 
		{
			var separator = $("li#sep_"+index+"_"+(i+1));
			if(separator.length) { //update existing value
				separator.text(values[i]);
			}
			else { //add new separator 
				$("#static_" + index).append('<li id="sep_'+ index +'_'+ (i+1) +'">'+ values[i] +'</li>');
			}
		}
	}

	function updateValue (ui) {
		var cm_val = ((parseInt(ui.value))*leds_interval)+0.5;
		cm_val = Math.round(cm_val*10)/10;
		nb_leds = parseInt(ui.value)+1;
		//console.log('led number', nb_leds);
	    $(ui.handle).attr('data-value', cm_val + " cm"); //Math.round(ui.value*1.63*100)/100 + " cm");
	};

	function getSlideElements() {
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

	 	return JSON.stringify(lines);
	}

	$("#saveStaticPositions").on('click', function() {
	 //'/module/<app_id>'
	 	var elements = getSlideElements();
	 	//console.log(elements);

		$.ajax({
			dataType: 'json',
        	contentType: 'application/json',
			data: elements,
		    type: 'POST',
		    url: $("#formEditArduino").attr('action')+'?mode=save',
		    complete: function() {
		    	$('#alertPreview').hide();
		    	$('#alertSave').show();		    	
		    }
		});
	});

	$("#previewStaticPositions").on('click', function() {
	 	var elements = getSlideElements();
	 	//console.log(elements);

		$.ajax({
			dataType: 'json',
        	contentType: 'application/json',
			data: elements,
		    type: 'POST',
		    url: $("#formEditArduino").attr('action')+'?mode=preview',
		    complete: function() {
		    	$('#alertPreview').show();
		    	$('#alertSave').hide();	
		    }
		});
	});	

	$('#colorEditor-save').on('click', function() {
		var c = getColor();
		$('input[name="mood_color"]').val(c);
		$('#rgbText').text("RGB code update");
	});

});
