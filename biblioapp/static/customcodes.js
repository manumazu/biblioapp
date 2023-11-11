$(document).ready(function() {

	// manage save customcode order list 
  	$('#save-order').hide();

    $( "#code-sortable tbody" ).sortable({
    	stop: function(e, ui) {
		    $('#save-order').removeClass('btn-success');
		    $('#save-order').text('Save changes');	    		
    		$('#save-order').show();
    	}
	});

	$('#save-order').on('click', function() {
	  	var elements = $( "#code-sortable tbody" ).sortable('serialize');
	  	//console.log('elements', elements);
	 	elements = elements+'&customcode=1';    
		ajax_postOrder(elements, this);
	});

});

// before delete
function checkPublished(isPublished) {
	var str = "";
	if(isPublished==1)
		str += "This code is published. ";
	str += "Are you sure ?";
	var r = confirm(str);	
	return r;
}