$(document).ready(function() {

	$('#customCodePreview').hide();

	$('#btn-customcode_update').hide();	
	if($('input[name="colorCode_val"]').val() != 'color') 
		$('#rgbCode').hide();

	var code_id = $('input[name="code_id"]').val(); // key for update object	

	$('input[name="colorCode_val"]').on('change', function() {
		if($('input[name="colorCode_val"]').val() == 'color') 
			$('#rgbCode').show();
		else
			$('#rgbCode').hide();
	});

	//blink mode is available for incrementation only
	if($('input[name="direction"]:checked').val()=='on2off') {
		$('#blink-mode').hide();
		$('#blinkled').text('');
		$('#blinkstrip').text('');	
	}
	$('input[name="direction"]').on('change', function() {
		if($('input[name="direction"]:checked').val()=='off2on')
			$('#blink-mode').show();
		else {
			$('#blink-mode').hide();
			$('#blinkled').text('');
			$('#blinkstrip').text('');				
		}
	});

	//preview code
	$('#btn-customcode_preview').on('click', function() {

		//customvars
		var nbLeds_val = $('input[name="nbLeds_val"]').val();
		var offset_val = $('input[name="offset_val"]').val();
		var start_val = $('input[name="start_val"]').val();	
		var nbStrips_val = $('input[name="nbStrips_val"]').val();	
		var colorCode_val = $('input[name="colorCode_val"]').val();	
		var rgbCode_val = 0;
		if($('input[name="rgbCode_val"]').val() != '')
			rgbCode_val = $('input[name="rgbCode_val"]').val();
		var delay_val = $('input[name="delay_val"]').val();	

		$('#nbLeds_val').html(nbLeds_val);
		$('#offset_val').html(offset_val);
		$('#start_val').html(start_val);
		$('#nbStrips_val').html(nbStrips_val);
		$('#colorCode_val').html("'"+colorCode_val+"'");
		$('#rgbCode_val').html("'"+rgbCode_val+"'");
		$('#delay_val').html(delay_val);

		//manage loops : increment or decrement leds
		var direction = $('input[name="direction"]:checked').val();			
		var off2on = "for(n=start; n<nbLeds; n+=offset)";
		var on2off = "for(n=nbLeds; n>start; n-=offset)";
		var msg2off = "app.setBlockMessage(n-offset, strip, offset, 'down', rgb);";
		var msg2on = "app.setBlockMessage(n, strip, offset, color, rgb);";
		$('#forleds').text(eval(direction));
		$('#forstrip').text(eval(direction));
		if(direction=='on2off') {
			$('#showAll').show();
			$('#msgstrip').text(msg2off);
			$('#msgleds').text(msg2off);
		}
		else {
			$('#showAll').hide();
			$('#msgstrip').text(msg2on);
			$('#msgleds').text(msg2on);			
		}

		//blink mode is available for incrementation only
		if(direction=='off2on') {
			var blink = $('input[name="blink"]:checked').val();
			var blink_val = "app.setBlockMessage(n, strip, offset, 'down', rgb);\n\t\tawait timer(delay);"	
			if(blink=='on') {
				$('#blinkled').text(blink_val);
				$('#blinkstrip').text(blink_val);
			}
			if(blink=='off') {
				$('#blinkled').text('');
				$('#blinkstrip').text('');
			}

		}

		//show preview
		var loop_priority = $('input[name="loop_priority"]:checked').val();
		if(loop_priority=='ledsfirst')
			$('#stripfirst').hide();
		if(loop_priority=='stripfirst')
			$('#ledsfirst').hide();		
		$('#'+loop_priority).show();

		$('#customCodePreview').show();		

		//hide old version
		if(code_id != 0) {
			$('#customCodeCurrent').hide();
		}
		//show save button		
		$('#btn-customcode_update').show();
	});


	$('#btn-customcode_update').on('click', function() {

		var elements = new Object();
		var loop_priority = $('input[name="loop_priority"]:checked').val();

		elements['title'] = $('input[name="code_title"]').val();
		elements['description'] = $('textarea[name="description"]').val();
		//elements['customcode'] = "async function cc() {" + $('#customvars').text()+''+$('#'+loop_priority).text() + "} \ncc();";
		
		elements['customcode'] = $('#customvars').text();
		var direction = $('input[name="direction"]:checked').val();
		if(direction=='on2off') {
			elements['customcode'] += '\n'+$('#showAll').text();
		}
		elements['customcode'] += '\n'+$('#'+loop_priority).text();


		//console.log(elements['customcode']);return;

		var customvars = new Object();
		customvars['nbLeds_val'] = $('input[name="nbLeds_val"]').val();
		customvars['offset_val'] = $('input[name="offset_val"]').val();
		customvars['start_val'] = $('input[name="start_val"]').val();
		customvars['nbStrips_val'] = $('input[name="nbStrips_val"]').val();
		customvars['colorCode_val'] = $('input[name="colorCode_val"]').val();
		customvars['rgbCode_val'] = $('input[name="rgbCode_val"]').val();
		customvars['delay_val'] = $('input[name="delay_val"]').val();
		customvars['blink'] = $('input[name="blink"]:checked').val();		
		customvars['direction'] = $('input[name="direction"]:checked').val();		
		customvars['loop_priority'] = loop_priority;
		elements['customvars'] = customvars;

		dest_url = '/customcodes/'; // new object
		if(code_id != 0) {
			dest_url = '/customcode/'+code_id; // update current object
		}

		$.ajax({
	  	      data: JSON.stringify(elements),
	  	      type: 'POST',
	  	      contentType: 'application/json',
	  	      url: dest_url, 
	  	      dataType: 'json',
	  	      complete: function(res){ window.location='/customcodes/?saved='+code_id; }
	      });
	});


	$('#colorEditor-save').on('click', function() {
		var c = getColor();
		$('input[name="rgbCode_val"]').val(c);
		$('#rgbText').text("RGB code update");
	});

});
