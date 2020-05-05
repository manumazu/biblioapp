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
              $(drop_selector).append('<li id="book_'+book[1]['id']+'" class="ui-state-default"> \
                <a href="'+book[1]['url']+'">'+book[1]['author']+' - '+book[1]['title']+'</li>');
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
    var elements = $(current_selector).sortable('serialize');
    var row = current_selector.split('_')[1];
    ajax_postOrder(elements,row);
  });

  $('#tags').tagEditor({
      autocomplete: { delay: 0, position: { collision: 'flip' }, source: urlAjaxCategories },
      forceLowercase: false,
      placeholder: 'book categories',
      initialTags: bookCategories
    });

    //search book to be permuted with
    $( "#keyword" ).autocomplete({
      source: function( request, response ) {
        $.ajax( {
          url: "/ajax_search/",
          data: {
            term: request.term
          },
          success: function( data ) {
            response( data );
          }
        } );
      },
      minLength: 3,
      select: function( event, ui ) {
        $("#permute_book_id").val(ui.item.id);
        $("#permute_book_title").val(ui.item.value);
      }
    } ); 

  //send permutation request
  $("#permute_action").on('click', function() {
    var permute_book_id = $("#permute_book_id").val();
    var permute_book_title = $("#permute_book_title").val();
    var book_id = $('input[name="book_id"]').val();
    var book_title = $('input[name="title"]').val();
    if(book_id>0 && permute_book_id>0) 
    {
      $.ajax({
            data: 'dest_id='+permute_book_id+'&from_id='+book_id,
            type: 'GET',
            url: '/ajax_permute_position/', //get items by position for given shelf 
            dataType: 'json',
            complete: function(res)
            {
              console.log(res.responseText);
              var json=$.parseJSON(res.responseText);
              if(book_id == permute_book_id) {
                alert("Error : book can not be permuted on itself");
              }
              else if(json.success == false && json.dest_range !== undefined) {
                var range = $("#range-adjust option:selected").val();
                alert("Error : destination book interval is " + json.dest_range + " and current is "+range);
              }
              else if(json.success == true) {
                alert("Permutation ok for : \"" + book_title + "\" <-> \"" + permute_book_title + "\"");
                window.location = '/app/'
              }
            }
      });
    }
  });

  $("#range-adjust").on('change', function() {

    var book_id = $('input[name="book_id"]').val();
    var range = $("#range-adjust option:selected").val();
    var column = $('input[name="column"]').val();
    var row = $('input[name="row"]').val();
    //set new position for given new range
    var r = confirm("This change will affect all positions in shelf number " + row);
    if (r == true) {
        $.ajax({
            data: 'book_id='+book_id+'&range='+range+'&column='+column+'&row='+row,
            type: 'POST',
            url: '/ajax_set_position/',
        });
        //get list of books for current row
        $.ajax({
              data: 'row='+row,
              type: 'GET',
              url: '/ajax_positions_inline/', //get items by position for given shelf 
              dataType: 'json',
              complete: function(res)
              {
                var json=$.parseJSON(res.responseText);
                var elements = [];
                $.each(json, function(key,elem){
                  elements.push('book[]='+elem[1]['id']);
                });
                params = elements.join('&');
                //sort list again
                ajax_postOrder(params,row);
              }
        });
    }

  });

  $('#form-del-book').on('submit', function() {
    var res = confirm('Are you sure ?');
    return res;
  });

});
