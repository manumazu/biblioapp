$(document).ready(function() {

	$('#customCodePreview').hide();
	$('#btn-customcode_update').hide();	

	var code_id = $('input[name="code_id"]').val(); // key for update object

	//preview code
	$('#btn-customcode_preview').on('click', function() {

		//customvars
		var nbLeds_val = $('input[name="nbLeds_val"]').val();
		var offset_val = $('input[name="offset_val"]').val();
		var nbStrips_val = $('input[name="nbStrips_val"]').val();	
		var colorCode_val = $('input[name="colorCode_val"]').val();	

		$('#nbLeds_val').html(nbLeds_val);
		$('#offset_val').html(offset_val);
		$('#nbStrips_val').html(nbStrips_val);
		$('#colorCode_val').html("'"+colorCode_val+"'");

		//show preview
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
		elements['title'] = $('input[name="code_title"]').val();
		elements['customcode'] = $('#customCodePreview').text();

		var customvars = new Object();
		customvars['nbLeds_val'] = $('input[name="nbLeds_val"]').val();
		customvars['offset_val'] = $('input[name="offset_val"]').val();
		customvars['nbStrips_val'] = $('input[name="nbStrips_val"]').val();
		customvars['colorCode_val'] = $('input[name="colorCode_val"]').val();
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
	  	      complete: function(res){ alert('code saved'); }
	      });
	});

});
