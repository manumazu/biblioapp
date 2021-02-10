$(document).ready(function() {

	$('#alertPreview').hide();	
	$('#alertSave').hide();

	//init sliders
	$(sliderList).each(function(i, static) {
		//console.log(static);
    	var handler = [];
		i++;
		$("#"+static+" li").each( function(index) {
			var val = $(this).text();
			if($.isNumeric(val)) {
				handler.push(val);			
			}
		});
		
		$("#add_"+i).on('click', function(){
			handler.push("0");
			$("#slider_"+i).slider("destroy");
			setSlider(i, handler);
		});

		//remove last position value in slider
		$("#remove_"+i).on('click', function(){
			if(handler.length > 1) {
				handler.pop();
				updatePositionValues(i, handler);	
				updateSliderColors(i);
			}
			else {
				alert("No less than one color");
			}
			$("#slider_"+i).slider("destroy");
			setSlider(i, handler);
		});

		if(!handler.length){
			handler.push("0");
		}

		setSlider(i, handler);
 	});


	function setSlider ( index, values) {	
		//sliders.slider_num = index;
		$("#slider_" + index).slider({
		  min: 0,
		  max: parseInt(nb_cols)-1,
		  animate: true,
		  values: values,
		  change: function( event, ui ) {
		  	if(ui.values) {
				//update values	
				updatePositionValues(index, ui.values);	
				//display colorpicker
				colorEditor('new_color_' + index + '_' + (ui.handleIndex+1));				
				//update css colors
				updateSliderColors(index);
		  	}
		  },
	      create: function (event, ui) {
	        $.each( values, function(i, v){
	            updateValue({
	                value: v,
	                handle: $('#slider_'+index+' .ui-slider-handle').eq(i) 
	            });
	        });
	        //updateSliderColors(index);
	      },  
	      slide: function (event, ui) {
	        updateValue(ui);
			var current_color = $('#new_color_' + index + '_' + (ui.handleIndex+1)).val();
			updateSliderColors(index);
		  }
		});
		//init colors
		updateSliderColors(index);
	}

	function updateSliderColors(index) {
		var colorstops = "";
		var arrcol = getSlideElements(index);
		//console.log('arrcol',arrcol);

		if(arrcol.length) {
			//sort colors by position
			arrcol.sort(function(a, b) {
			  return a.handle - b.handle;
			});
		}
		else { //init color with grey
			let obj = {handle: 0, color:'#4e5d6c'};
			arrcol.push(obj);	
		}

		//manage colors order in css
		var colorstops = arrcol[0].color + ", "; // start left with the first color
        for (var i=0; i< arrcol.length; i++) {
        	var perc = (arrcol[i].handle/(nb_cols-1))*100;
        	if(arrcol[i] != undefined)
            	colorstops += arrcol[i].color + " " + perc + "%,";
            if(arrcol[i+1] != undefined)
	            colorstops += arrcol[i+1].color + " " + perc + "%,";
        }
        // end with the last color to the right
        if(perc == 100)
	        colorstops += arrcol[arrcol.length-1].color;
	    else { //fill with grey color when line is not finished
	    	colorstops += "#4e5d6c " + perc + "%, #4e5d6c";
	    }

		var css = '-webkit-linear-gradient(left,' + colorstops + ')';
		//console.log('current_color', css);
        $('#slider_'+index).css('background-image', css);
	}

	function updatePositionValues(index, values) 
	{
		//console.log('update', values);
		//backup
		var backupcolors = [];
		for(i=0;i<values.length;i++) 
		{
			var separator = $("li#sep_"+index+"_"+(i+1));
			var curcolor = $("#new_color_"+index+"_"+(i+1)).val();
			backupcolors.push(curcolor);
		}
		//clean
		var element = $('#static_' + index);
		element.html("");
		//populate	
		for(i=0;i<values.length;i++) {
			element.append('<li id="sep_'+ index +'_'+ (i+1) +'">'+ values[i] +'</li>');
			element.append('<input type="text" id="new_color_'+ index +'_'+ (i+1) +'" name="custom_color" value="' + backupcolors[i] + '">');			
		}
	}

	function updateValue (ui) {
		var cm_val = ((parseInt(ui.value))*leds_interval)+0.5;
		cm_val = Math.round(cm_val*10)/10;
		nb_leds = parseInt(ui.value)+1;
		//console.log('led number', nb_leds);
	    $(ui.handle).attr('data-value','LED n°' + nb_leds + ' (' + cm_val + " cm)"); //Math.round(ui.value*1.63*100)/100 + " cm");
	};

	function getSlideElements(elem = null) {

		var lines = new Object();
		$(sliderList).each(function(index, static) {

			var arrcol = [];
			
			//get rgb values
			$('#'+static + ' input[name="custom_color"]').each( function(i) {
				//console.log('list colors', $(this).val());
				//console.log('list values', values[i]);

				//init handle color grey
				let rgb = '#4e5d6c';
				if($(this).val()!="") {
					rgb = 'rgb('+$(this).val()+')';
				}
				let obj = {handle: $('#sep_' + (index+1) + '_'+(i+1)).text(), color:rgb};
				arrcol.push(obj);
			});	

			//if(arrcol.length)
			lines[index] = arrcol;

		});	
		//console.log('lines', lines);

		if(elem != null)
		 	return lines[elem-1]; //return part off array
		return lines;
		//JSON.stringify(lines);
	}

	$('#colorEditor-save').on('click', function() {
		var c = getColor();
		var dest = $('#destination').val(); //get field name which store color value
		if(dest !== '') {
			$('#' + dest).val(c);
			//extract current slider handle value
			let index = dest.split('_')[2];
			//console.log($('#sep_' + ids[2] + '_' + ids[3]).text());
			updateSliderColors(index);
		}
		else
			$('input[name="custom_color"]').val(c);
		$('#rgbText').text("RGB code update");
	});	

	$("#removeStaticPositions").on('click', function() {
	 //'/module/<app_id>'
	 	var res = confirm('Are you sure ?');
	 	if (res) {
		 	var elements = getSlideElements();
		 	//console.log(elements);
			$.ajax({
				dataType: 'json',
	        	contentType: 'application/json',
				data: elements,
			    type: 'POST',
			    url: $("#formEditArduino").attr('action')+'?mode=remove',
			    complete: function() {
			    	$('#alertPreview').hide();
			    	$('#alertSave').show();
			    	//reload page
			    	window.location = $("#formEditArduino").attr('action');	
			    }
			});
		}
	});



	$("#saveStaticPositions").on('click', function() {
	 //'/module/<app_id>'
	 	var elements = getSlideElements();
	 	//console.log(elements);

		$.ajax({
			dataType: 'json',
        	contentType: 'application/json',
			data: elements,
		    type: 'POST',
		    url: $("#formCustomColors").attr('action')+'?mode=save',
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
		    url: $("#formCustomColors").attr('action')+'?mode=preview',
		    complete: function() {
		    	$('#alertPreview').show();
		    	$('#alertSave').hide();	
		    }
		});
	});	

});
