$(document).ready(function() {

  $('#shelf-num').hide();
  $('#droppable_0').hide();
  $('#save-pos').hide();
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
        $(drop_selector).append('<li id="book_'+bookid+'" class="ui-state-highlight"> \
          <a href="'+book_url+'">'+book_author+' - '+book_title+'</li>');
        $(drop_selector).show();      
        //change droppable id
        $(drop_selector).attr('id', "droppable_"+shelfnum);
        var current_selector = '#'+$(drop_selector).attr('id');  
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
                <a href="'+book['url']+'">'+book['author']+' - '+book['title']+'</li>');
            });
            //ajax_postOrder(current_selector); //add new item
  	      }
	      });

      }
    });
  });

  $(drop_selector).sortable({
      //items: "li",
      /*update: function(e, ui) {
        //get id for current shelf element
      },*/
      stop: function(e, ui) {
        $('#save-pos').show();
      }
  });
  $(drop_selector).disableSelection();

  $('#save-pos').on('click', function() {
    var current_selector = '#'+$(drop_selector).attr('id'); 
    ajax_postOrder(current_selector);
  });

});
