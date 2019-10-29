$(document).ready(function() {

    /*var selectedClass = 'ui-state-highlight', 
        clickDelay = 600,
        // click time (milliseconds)
        lastClick, diffClick; // timestamps

    $("#draggable li")
    // Script to deferentiate a click from a mousedown for drag event
    .bind('mousedown mouseup', function(e) {
        if (e.type == "mousedown") {
            lastClick = e.timeStamp; // get mousedown time
        } else {
            diffClick = e.timeStamp - lastClick;
            if (diffClick < clickDelay) {
                // add selected class to group draggable objects
                $(this).toggleClass(selectedClass);
            }
        }
    })
    .draggable({
        revertDuration: 10,
        // grouped items animate separately, so leave this number low
        containment: '.demo',
        start: function(e, ui) {
            ui.helper.addClass(selectedClass);
        },
        stop: function(e, ui) {
            // reset group positions
            $('.' + selectedClass).css({
                top: 0,
                left: 0
            });
        },
        drag: function(e, ui) {
            // set selected group position to main dragged object
            // this works because the position is relative to the starting position
            $('.' + selectedClass).css({
                top: ui.position.top,
                left: ui.position.left
            });
        }
    });

    $("#droppable, #draggable").sortable().droppable({
        hoverClass: "ui-state-hover",
        drop: function(e, ui) {
            $('.' + selectedClass).appendTo($(this)).add(ui.draggable) // ui.draggable is appended by the script, so add it after
            .removeClass(selectedClass).css({
                top: 0,
                left: 0
            });
        }
    });
   //$("#droppable").disableSelection();*/

   var draggableElementsSize1 = $('#draggable li').size(), selectedClass = 'ui-state-default';
   var i1 = 0;

   $("#droppable").droppable({
      scope: "d1",
      activeClass: "ui-state-default",
      hoverClass: "ui-state-hover",
      accept: '#draggable li',
      drop: function( event, ui ) {
        i1++;
        ui.draggable.draggable('option','revert',false); 
	ui.draggable.clone().appendTo(this);
        ui.draggable.remove();
     }
     }).sortable({
      items: "li",
      sort: function() {
        $( this ).removeClass("ui-state-default");
      }
   });

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

   $("#droppable").sortable({
	update: function(e, ui) {
	// POST to server using $.ajax
	var order = $('#droppable').sortable('serialize'); 
	console.log(order);
	/*$.ajax({
	    data: order,
	    type: 'POST',
	    url: ''
	});*/
       }
   });

});
