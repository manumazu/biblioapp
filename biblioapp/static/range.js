$(document).ready(function() {

	$('#save-order').hide();

   	//set chosen shelf for session
   	$('.nav-pills .nav-link').on('click', function() {
	   	var shelfnum = $(this).attr('href').split('_')[1];
	   	console.log(shelfnum);
		$.ajax({
	  	      data: 'rownum='+shelfnum,
	  	      type: 'GET',
	  	      url: '/ajax_set_bookshelf/', //get items by position for given shelf
		});
   	});

   	//change positions
   	var selectedClass = 'ui-state-default';//, droppableElements=['#droppable_1', '#droppable_2', '#droppable_3'];
   	var i = 0;
   	var order = [];

   	if(typeof droppableElements!='undefined') 
   	{
	   	droppableElements.forEach(function(element) 
	   	{ 
		   	$(element).droppable({
			      scope: "d1",
			      activeClass: "ui-state-default",
			      hoverClass: "ui-state-hover",
			      accept: '#draggable li',
			      drop: function( event, ui ) {
					i++;
					ui.draggable.remove();
					ui.draggable.detach().css({top: 0,left: 0}).appendTo($(this));
			 
					//specific event after dropped item
				    var elements = $(element).sortable('serialize');			    
				    var row = element.split('_')[1];
				    elements = elements+'&row='+row;
					ajax_postOrder(elements); //order new item

					ui.draggable.find('span').one('click', function() { //delete new item
					   ajax_supprItem($( this ));
					});
			     },
			}).sortable({
			      items: "li:not(.non-draggable)",
			      sort: function() {
					$( this ).removeClass("ui-state-default");
			      },
			      stop: function(e, ui) {
			      	$('#save-order').removeClass('btn-success');
			      	$('#save-order').text('Save changes');
			        $('#save-order').show();
			      },
			      placeholder: "highlight",
		   	});

		   	/*$(element).delay( 1000 ).sortable({
				update: function(e, ui) {
					var elements = $(element).sortable('serialize');
			    	var row = element.split('_')[1];
					ajax_postOrder(elements,row);					
		   		}
		   	});*/

			//remove book from list
			$(element+" li span").one('click', function() {
				ajax_supprItem($( this ));
			});

			//save order for current shelf active
			$('#save-order').on('click', function() {
				if($(element).hasClass('active')) {
				    var current_selector = '#'+$(element).attr('id'); 
				    var elements = $(element).sortable('serialize');
				    var row = current_selector.split('_')[1];	
				    //console.log(elements);
				    elements = elements+'&row='+row;    
				    ajax_postOrder(elements, this);
				}
			});

	   	});
	}

  	$('#draggable li').draggable({
	    appendTo: "body",
	    //helper: "clone",
	    revert: true,
	    scope: "d1",
	    cursor: 'move',
	    start: function(e, ui) {
	       ui.helper.addClass(selectedClass);
	    },
	    stop: function(e, ui) {
	      // reset group positions
	      $('.' + selectedClass).css({
	        top: 0,
	        left: 0
	      });
	    }
   	});

});

//update values for bookshelf + capacity alert 
function updateBookshelf(res) {
  	var lastBookFulfillment = 0;
    var currentShelf = 0;
  	for(var i=0; i<res.length;i++) {
	  	lastBookFulfillment = res[i]['fulfillment'];
	  	currentShelf = res[i]['shelf'];
	}
	
	if(lastBookFulfillment > maxColsShelf) {
	  	alert('Shelf capacity is exceeded !');
	}
	//update fulfillment progress bar	
	var statics = JSON.parse(json_statics);
	//adjust progress with static position
	if(lastBookFulfillment < statics[0]['led_column'])
		lastBookFulfillment+=statics[0]['range'];
	var new_progress_value = Math.round((lastBookFulfillment/maxColsShelf)*100);
	console.log(new_progress_value);
	$('#shelf_progress_'+currentShelf).attr('aria-valuenow', new_progress_value);
	$('#shelf_progress_'+currentShelf).css('width', new_progress_value + '%');
	$('#shelf_progress_'+currentShelf).text('Fulfillment ' + new_progress_value + '%');
}
