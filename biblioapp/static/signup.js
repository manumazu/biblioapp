//init validation vars
var allowSubmit = false;
var pwdOk = false;
var emailOk = false;
var captchaOk = false;
var nameOk = false;
var uemailMsg = '';

$(document).ready(function() {
	//store message for callback validation
	uemailMsg = $('#uemailHelp').text();
	//check form during field fill
	validForm();
});

//callback function for captcha, used for form validation
function onSubmit(token) {

    ajax_validRecaptcha(token).then(function(res, e)
    {
    	if(res=='ok') {
    		captchaOk = true;
    		$('#recaptchaHelp').hide();
    	}
    	else {
    		captchaOk = false;
    		$('#recaptchaHelp').show();
    	}

		nameOk = checkName('#ufirstname');
		emailOk = checkEmail('#uemail');
		pwdOk = checkPwd('#upassword');

		allowSubmit = validForm();

		if(allowSubmit) { //start submit
			var url = $("#form-signUp").attr('action');
			submitForm(url);
		}    	

    });

}

//ajax submit data 
function submitForm(url) {
	var dataStr = 'ufirstname='+$('#ufirstname').val().trim()+'&ulastname='+$('#ulastname').val().trim();
	dataStr += '&uemail='+$('#uemail').val().trim()+'&upassword='+$('#upassword').val().trim();
	$.ajax({
		    data: dataStr,
		    type: 'POST',
		    url: url,
		    complete: function(res){
		    	console.log(res.responseText);
		    	var json=$.parseJSON(res.responseText);
		    	 if(json.success == false){
		    	 	if(json.field !== undefined) {
		    	 		$('#'+json.field).addClass('is-invalid').removeClass('is-valid');
		    	 		$('#'+json.field+'Help').text(json.message).show();
		    	 	}
		    	 	else {
		    	 		alert("Error during process, please retry to submit");
		    	 	}
		    	 }
		    	 if(json.success == true){
		    	 	if(json.redirect !== undefined)
		    	 		window.location = json.redirect+'?saved=true';
		    	 }
		    }
	});
}

//fileds formats validation
function validForm() {

	$('#passwordconfirm').blur(function() {pwdOk = checkPwd(this);});
	$('#uemail').on('input', function() {emailOk = checkEmail(this);});
	$('#ufirstname').on('input', function() {nameOk = checkName(this);});
	if(pwdOk && emailOk && captchaOk && nameOk) {
		return true;	
	}
	return false;
}

function checkName(elem) {
	if($(elem).val().length == 0 && $('#ulastname').val().length == 0) {
		$(elem).addClass('is-invalid').removeClass('is-valid');
		$('#ulastname').addClass('is-invalid').removeClass('is-valid');
		$('label[for="ufirstname"]').addClass('text-danger').removeClass('text-success');		
		return false;	
	}
	else {
		$(elem).addClass('is-valid').removeClass('is-invalid');
		$('#ulastname').addClass('is-valid').removeClass('is-invalid');	
		$('label[for="ufirstname"]').addClass('text-success').removeClass('text-danger');
		return true;			
	}
}

function checkPwd(elem) {
	//check password
	if(  $('#upassword').val().length < 4 || $('#upassword').val() != $(elem).val()) {
		$('#upassword').addClass('is-invalid').removeClass('is-valid');
		$(elem).removeClass('is-valid');
		$('label[for="upassword"]').addClass('text-danger').removeClass('text-success');
		$('#passwordHelp').show();
		return false;
	}
	else if($('#upassword').val().length > 3 && $('#upassword').val() == $(elem).val()){
		$('#upassword').addClass('is-valid').removeClass('is-invalid');
		$(elem).addClass('is-valid');
		$('label[for="upassword"]').addClass('text-success').removeClass('text-danger');
		$('#passwordHelp').hide();
		return true;
	}
}

function checkEmail(elem) {
	var re = /^\w+([-+.'][^\s]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$/;
	var emailFormat = re.test($(elem).val());
	if (!emailFormat) {
		$(elem).addClass('is-invalid').removeClass('is-valid');
		$('label[for="uemail"]').addClass('text-danger').removeClass('text-success');
		$('#uemailHelp').text(uemailMsg).show();
		return false;
	}
	else {
		$(elem).addClass('is-valid').removeClass('is-invalid');
		$('label[for="uemail"]').addClass('text-success').removeClass('text-danger');		
		$('#uemailHelp').hide();
		return true;
	}
}

//server side recaptcha valdiation
function ajax_validRecaptcha(token) {
	return new Promise(function(resolve, reject) {
	    $.ajax({
		    data: "token="+token,
		    type: 'POST',
		    url: '/ajax_recaptcha/',
		    success: function(res){
		    	console.log('validRecaptcha',res);
		    	resolve(res);
		    },
		    error: reject
	    });
	});
}