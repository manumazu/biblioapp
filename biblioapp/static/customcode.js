$(document).ready(function() {

	$('#customCodePreview').hide();

	var code_id = $('input[name="code_id"]').val();

	$('#customcode_update').on('click', function() {

		var nbLeds_val = $('input[name="nbLeds_val"]').val();
		$('#nbLeds_val').html(nbLeds_val);

		var offset_val = $('input[name="offset_val"]').val();
		$('#offset_val').html(offset_val);

		var nbStrips_val = $('input[name="nbStrips_val"]').val();
		$('#nbStrips_val').html(nbStrips_val);

		var colorCode_val = $('input[name="colorCode_val"]').val();
		$('#colorCode_val').html("'"+colorCode_val+"'");

		$('#customCodePreview').show();
		//hide old version
		$('#customCodeCurrent').hide();

		$.ajax({
	  	      data: JSON.stringify($('#customCodePreview').text()),
	  	      type: 'POST',
	  	      contentType: 'application/json',
	  	      url: '/customcode/'+code_id, 
	  	      dataType: 'json',
	  	      complete: function(res){ alert('code saved'); }
	      });
	});

});
