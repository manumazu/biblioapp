$(document).ready(function() {

  $('#shelf-num').hide();
  $('a[id^="rangebook"]').on('click', function() {
    
    var bookid = $(this).attr("id").match(/\d+$/);
    //display book for select book shelf
    $('#shelf-num').show();
    $('#select-shelf').change(function() {
      var shelfnum = $( "#select-shelf option:selected" ).val();
      if($.isNumeric(shelfnum)) {
        $.ajax({
	      data: 'row='+shelfnum,
	      type: 'GET',
	      url: '/ajax_positions_inline/', //get items by position for given shelf 
	      dataType: 'json',
	      complete: function(res){
		var json=$.parseJSON(res.responseText);
		$.each(json, function(key,value){
                   console.log(key+" -- "+value);
               });
	      }
	});
      }
    });
  });
  

});
