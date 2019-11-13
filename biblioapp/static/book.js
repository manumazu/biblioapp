$(document).ready(function() {

  $('#shelf-num').hide();
  $('#droppable_0').hide();
  var drop_selector = 'ul[id^="droppable"]';

  $('a[id^="rangebook"]').on('click', function() 
  {
    var bookid = $(this).attr("id").match(/\d+$/);
    //display book for select book shelf
    $('#shelf-num').show();
    $('#select-shelf').change(function() {
      var shelfnum = $( "#select-shelf option:selected" ).val();
      if($.isNumeric(shelfnum)) 
      {
        $(drop_selector).html('');//clear list
        //add current book to list
        $(drop_selector).append('<li><span class="del">x</span><a href="'+book_url+'"> \
          '+book_author+' - '+book_title+'</li>');
        $(drop_selector).show();        
        //change droppable id
        $(drop_selector).attr('id', "droppable_"+shelfnum);
        //add other books for current shelf
        $.ajax({
  	      data: 'row='+shelfnum,
  	      type: 'GET',
  	      url: '/ajax_positions_inline/', //get items by position for given shelf 
  	      dataType: 'json',
  	      complete: function(res){
  		      var json=$.parseJSON(res.responseText);
  		      $.each(json, function(key,book){
              $(drop_selector).append('<li id="book_'+book['id']+'" class="ui-state-default"> \
                <span class="del">x</span><a href="'+book['url']+'">'+book['author']+' - '+book['title']+'</li>');
            });
  	      }
	      });

      }
    });
  });

  $(drop_selector).sortable();
  $(drop_selector).disableSelection();

});
