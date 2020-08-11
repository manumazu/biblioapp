$(document).ready(function() {

	$('#save-order').hide();

	//get selected shelf onload 
	var selectedShelf = getSelectedShelf();
	//update progress bar
	setProgressValue(selectedShelf);		

   	//set chosen shelf for session
   	$('.nav-pills .nav-link').on('click', function() {
	   	var selectedShelf = $(this).attr('href').split('_')[1];
	   	//update progress bar
	   	setProgressValue(selectedShelf);
		$.ajax({
	  	      data: 'rownum='+selectedShelf,
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
				if($(element).parent().hasClass('active')) {
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

//get selected shelf 
function getSelectedShelf() {
	var str = 0;
	$('.tab-pane').each(function() {
		if($(this).hasClass('active')) {
			str = $(this).attr('id').split('_')[1];
		}
	});
	return str;
}

//update values for bookshelf + capacity alert 
function updateBookshelf(res) {
  	var lastBookFulfillment = 0;
    var currentShelf = 0;
  	for(var i=0; i<res.length;i++) {
	  	lastBookFulfillment = res[i]['fulfillment'];
	  	currentShelf = res[i]['shelf'];
	}
	
	//check shelf capacity
	if(lastBookFulfillment > maxColsShelf) {
	  	alert('Shelf capacity is exceeded !');
	}

	//update fulfillment progress bar	
	var new_progress_value = Math.round((lastBookFulfillment/maxColsShelf)*100);
	//console.log('add',new_progress_value);

	//adjust progress rate with statics element positions
	var statics = JSON.parse(json_statics);
	if(statics[currentShelf] !== undefined) {
		var staticsRange = 0;
		for(var i=0; i < statics[currentShelf].length; i++){
			if(lastBookFulfillment < statics[currentShelf][i]['led_column'])
				staticsRange += statics[currentShelf][i]['range'];
		}
		var staticsElementRate =  Math.round((staticsRange/maxColsShelf)*100);
		new_progress_value += staticsElementRate;
	}
	//console.log('adjust',new_progress_value);
	
	setProgressValue(currentShelf, new_progress_value);
}

function setProgressValue(currentShelf, init_progress_value = 0) {

	
	if(init_progress_value == 0) { // init value with current progress
		init_progress_value = parseInt($('#shelf_progress_'+currentShelf).attr('aria-valuenow'));
	}
	var new_progress_value = init_progress_value;

	//console.log('new', new_progress_value);
	$('#shelf_progress_'+currentShelf).attr('aria-valuenow', new_progress_value);
	$('#shelf_progress_'+currentShelf).css('width', new_progress_value + '%');
	$('#shelf_progress_'+currentShelf).text('Fulfillment ' + new_progress_value + '%');	

	//display progress bar
	if(parseInt(init_progress_value) > 0) {
		$('#shelf_progress_'+currentShelf).parent().css('display','block');
	}
	//when no book left	
	if(isNaN(new_progress_value)) { 
		var currentShelf = getSelectedShelf();
		$('#shelf_progress_'+currentShelf).parent().css('display','none');
	}
}


function setEventListener(source, type) {
	var currentEventId = null;
	source.addEventListener("ping", function(event) {
    	var json = JSON.parse(event.data);
    	if(currentEventId != event.lastEventId && json.length>0) 
    	{
	      	//parse json and set or unset badges 
	      	json.forEach(function(elem) {
	      		//check source of event : server or mobile
	      		var type = 'S';
	      		if('client' in elem && elem['client']=='mobile')
	      			type = 'M';
	        	//add book request's badge for client mobile 
	        	if(elem['action']=='add') {
	          		elem['nodes'].forEach(function(id) {
	            		var node = $('#book_'+id);
	            		//if(node.find('span').hasClass('requested') == false) 
	              		node.append('<span class="badge badge-success badge-pill requested">' + type + '</span>');
	          		});
	        	}
	        	//remove request's badge for client mobile 
	        	if(elem['action']=='remove') {
	          		elem['nodes'].forEach(function(id) {
	            		var node = $('#book_'+id);
	            		//if(node.find('span').hasClass('requested') == true) 
	              		node.find('span').remove('.requested');
	          		});
	        	}
	     	});
      		console.log(event.data);
    	}
    	currentEventId = event.lastEventId;
    	return currentEventId;
  });
}
