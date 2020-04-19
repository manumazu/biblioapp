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

	//preview code
	$('#btn-customcode_preview').on('click', function() {

		//customvars
		var nbLeds_val = $('input[name="nbLeds_val"]').val();
		var offset_val = $('input[name="offset_val"]').val();
		var nbStrips_val = $('input[name="nbStrips_val"]').val();	
		var colorCode_val = $('input[name="colorCode_val"]').val();	
		var rgbCode_val = 0;
		if($('input[name="rgbCode_val"]').val() != '')
			rgbCode_val = $('input[name="rgbCode_val"]').val();

		$('#nbLeds_val').html(nbLeds_val);
		$('#offset_val').html(offset_val);
		$('#nbStrips_val').html(nbStrips_val);
		$('#colorCode_val').html("'"+colorCode_val+"'");
		$('#rgbCode_val').html("'"+rgbCode_val+"'");

		//show preview
		var loop_priority = $('input[name="loop_priority"]:checked').val();
		if(loop_priority=='ledsfirst')
			$('#stripfirst').hide();
		if(loop_priority=='stripfirst')
			$('#ledsfirst').hide();		
		$('#'+loop_priority).show();
		$('#customCodePreview').show();		

		//hide old version
		if(code_id !== undefined) {
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
		elements['customcode'] = $('#customvars').text()+''+$('#'+loop_priority).text();

		var customvars = new Object();
		customvars['nbLeds_val'] = $('input[name="nbLeds_val"]').val();
		customvars['offset_val'] = $('input[name="offset_val"]').val();
		customvars['nbStrips_val'] = $('input[name="nbStrips_val"]').val();
		customvars['colorCode_val'] = $('input[name="colorCode_val"]').val();
		customvars['rgbCode_val'] = $('input[name="rgbCode_val"]').val();
		customvars['loop_priority'] = loop_priority;
		elements['customvars'] = customvars;

		dest_url = '/customcodes/'; // new object
		if(code_id !== undefined) {
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
