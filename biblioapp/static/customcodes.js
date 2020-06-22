$(document).ready(function() {

	$('[data-toggle="tooltip"]').tooltip();

	//for new code
	var selected_template = '';
	$('#code-type .jumbotron').each(function() {
		//console.log($(this));
		if($(this).hasClass('active')) {
			selected_template = $(this).attr('id');
		}
	});

	//check if code already exists
	var code_id = $('input[name="code_id"]').val(); // key for update object
	if(code_id === undefined) {
		code_id = 0;
	}
	else { //for existing code 
		selected_template = $('input[name="template"]').val();
	}

	updateActiveCode(selected_template, code_id);

});

//choose template for new code
$('#code-selector .nav-item a').on('click', function() {
	var selected_template = $(this).attr('href').substring(1);
	updateActiveCode(selected_template, 0);
});

function updateActiveCode(selected_template, code_id) {

	//for new code load selected template
	if(code_id === 0) {

		//clean html template
		$('#code-type .jumbotron').each(function() {
			$(this).html('');
		});

		$.get( '/ajax_customcodetemplate/'+selected_template, function( data ) {
		  	$('#'+selected_template).html( data );
		  	editCodeForm(selected_template, 0);
		});
	}
	else { //for existing code, template is already loaded
		editCodeForm(selected_template, code_id);
	}
}

//manage form elements from templates
function editCodeForm(selected_template, code_id) {

	//console.log(selected_template);

	$('#customCodePreview').hide();

	$('#btn-customcode_draft').hide();	
	$('#btn-customcode_publish').hide();

	//manage form variables 
	if($('input[name="colorCode_val"]').val() != 'color') 
		$('#rgbCode').hide();

	$('input[name="colorCode_val"]').on('change', function() {
		if($('input[name="colorCode_val"]').val() == 'color') 
			$('#rgbCode').show();
		else
			$('#rgbCode').hide();
	});

	//preview code before saving
	var customvars = new Object();
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
		if(selected_template=='timer') {
			var blink = $('input[name="blink"]').val();	
			var loop_priority = $('input[name="loop_priority"]').val();
		}			
		else{
			var blink = $('input[name="blink"]:checked').val();
			var loop_priority = $('input[name="loop_priority"]:checked').val();
		}

		customvars['template'] = selected_template;
		customvars['nbLeds_val'] = nbLeds_val;
		customvars['offset_val'] = offset_val;
		customvars['start_val'] = start_val;
		customvars['nbStrips_val'] = nbStrips_val;
		customvars['colorCode_val'] = colorCode_val;
		customvars['rgbCode_val'] = rgbCode_val;
		customvars['delay_val'] = delay_val;
		customvars['blink'] = blink;			
		customvars['loop_priority'] =  loop_priority;	

		var validation = validForm(customvars);

		if (validation) {
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
			code.set_blink();
			code.print_code(loop_priority);	

			//hide old version
			if(code_id != 0) {
				$('#customCodeCurrent').hide();
			}
			else if(selected_template != 'wait') {
				$('#customCodePreview').css('top','-420px');		
			}
			//display new version
			$('#customCodePreview').show();		


			//show save button		
			$('#btn-customcode_draft').show();
			$('#btn-customcode_publish').show();
		}

	});


	$('#btn-customcode_draft').on('click', function() {
		saveCustomCode(code_id, customvars, false);
	});

	$('#btn-customcode_publish').on('click', function() {
		saveCustomCode(code_id, customvars, true);
	});


	$('#colorEditor-save').on('click', function() {
		var c = getColor();
		$('input[name="rgbCode_val"]').val(c);
		$('#rgbText').text("RGB code update");
	});

}

function saveCustomCode(code_id, customvars, published) {

	var elements = new Object();

	elements['title'] = $('input[name="code_title"]').val();
	elements['description'] = $('textarea[name="description"]').val();
	elements['published'] = published;
	elements['customcode'] = $('#customCodePreview').text();
	elements['customvars'] = customvars;

	//console.log(elements['customvars']);	

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

function validForm(customvars) {
	var totalLeds = parseInt(customvars['nbLeds_val'])*parseInt(customvars['nbStrips_val']);

	if(customvars['template']!='wait') 
	{
		if(customvars['loop_priority']===undefined) {
			alert("Your must choose a priority for loops (leds or strips first)");
			return false;
		}

		//alert(totalLeds);
		if(isNaN(totalLeds)) {
			alert("Give a LEDs value");
			return false;
		}

		if(isNaN(parseInt(customvars['offset_val']))) {
			alert("Give an offset value");
			return false;
		}

		if(totalLeds > max_leds) {
			alert("The total of " + totalLeds + " LEDs in your code is greater than the " + max_leds + " LEDs available in your strips.");
			return false;
		}

		var startLeds = totalLeds+parseInt(customvars['start_val']);
		if(startLeds > max_leds) {
			alert("Your script is starting after the " + max_leds + " LEDs available in your strips.");
			return false;	
		}
	}

	return true;
}