$(document).ready(function() {

	$('input[name="nb_lines"]').blur(function() {updateBleId()});
	$('input[name="striplength"]').blur(function() {updateBleId()});
	$('#ledspermeter').on('change',function() {updateBleId()});

	function updateBleId(elem) {
		var newLine = $('input[name="nb_lines"]').val();
		var moduleId = $('input[name="module_id"]').val();
		var stripLength = $('input[name="striplength"]').val();
		var ledsPerMeter = $('#ledspermeter option:selected').val();
		var nbLeds = Math.round(stripLength/(100/parseInt(ledsPerMeter))+0.5);

		var bibusId = 'bibus-';
		if( moduleId !== undefined )
			bibusId += ("0000" + moduleId).slice(-4)+'-';
		else
			bibusId += 'xxxx-';
		if(newLine > 0)
			bibusId += ("00" + newLine).slice(-2);	
		if(nbLeds > 0)
			bibusId+= ("000" + nbLeds).slice(-3);	

		$('input[name="id_ble"]').val(bibusId);
	}

	$('#formAdminArduino').submit(function(event) {
		var test = true;
		var msg = "";
		if($('#user option:selected').val()=='Firstname Lastname') {
			test = false;
			msg += "Firstname Lastname \n";
		}		
		if($('input[name="striplength"]').val()=='') {
			test = false;
			msg += "Strip length \n";
		}
		if($('input[name="nb_lines"]').val()=='') {
			test = false;
			msg += "Rows num \n";
		}		
		if($('#ledspermeter option:selected').val()=='Nb Leds') {
			test = false;
			msg += "Nb Leds \n";
		}		
		if(!test) {
			alert("These values are mandatory :\n"+msg);
			event.preventDefault();
		}
		else
			return;
	});

});
