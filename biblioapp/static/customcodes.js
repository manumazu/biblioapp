$(document).ready(function() {

	$('#customCodePreview').hide();

	$('#btn-customcode_draft').hide();	
	$('#btn-customcode_publish').hide();

	//manage form variables 
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
		$('#blink-mode *').prop('disabled',true);
		$('#blinkled').text('');
		$('#blinkstrip').text('');	
	}
	$('input[name="direction"]').on('change', function() {
		if($('input[name="direction"]:checked').val()=='off2on')
			$('#blink-mode *').prop('disabled',false);
		else {
			$('#blink-mode *').prop('disabled',true);
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
		if($('input[name="rgbCode_val"]').val() != '' && colorCode_val == 'color')
			rgbCode_val = $('input[name="rgbCode_val"]').val();
		var delay_val = $('input[name="delay_val"]').val();

		//manage loops : increment or decrement leds	
		var direction = $('input[name="direction"]:checked').val();		
		var blink = $('input[name="blink"]:checked').val();		
		var loop_priority = $('input[name="loop_priority"]:checked').val();
		//generate code with template object
		const code = Object.create(codegen);
		code.start = start_val; 
		code.nbLeds = nbLeds_val; 
		code.nbStrips = nbStrips_val;
		code.delay = delay_val; 
		code.offset = offset_val;
		code.color = colorCode_val;
		code.rgb = rgbCode_val;
		code.blink = blink;
		code.direction = direction;
		code.set_blink();
		code.print_code(loop_priority);

		//hide old version
		if(code_id != 0) {
			$('#customCodeCurrent').hide();
		}
		else {
			$('#customCodePreview').css('bottom','460px');		
		}
		//display new version
		$('#customCodePreview').show();		


		//show save button		
		$('#btn-customcode_draft').show();
		$('#btn-customcode_publish').show();
	});


	$('#btn-customcode_draft').on('click', function() {
		saveCustomCode(code_id, false);
	});

	$('#btn-customcode_publish').on('click', function() {
		saveCustomCode(code_id, true);
	});


	$('#colorEditor-save').on('click', function() {
		var c = getColor();
		$('input[name="rgbCode_val"]').val(c);
		$('#rgbText').text("RGB code update");
	});

});

function saveCustomCode(code_id, published) {

	var elements = new Object();
	//var loop_priority = $('input[name="loop_priority"]:checked').val();

	elements['title'] = $('input[name="code_title"]').val();
	elements['description'] = $('textarea[name="description"]').val();
	elements['published'] = published;
	elements['customcode'] = $('#customCodePreview').text();


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
	customvars['loop_priority'] =  $('input[name="loop_priority"]:checked').val();
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
}