$(document).ready(function() {

   var selectedClass = 'ui-state-default';
   var i = 0;

   $("#droppable").droppable({
      scope: "d1",
      activeClass: "ui-state-default",
      hoverClass: "ui-state-hover",
      accept: '#draggable li',
      drop: function( event, ui ) {
        i++;
        ui.draggable.draggable('option','revert',true); 
	ui.draggable.clone().appendTo(this);
        ui.draggable.remove();
        //$(ui.draggable).addClass('ui-sortable-handle');
     }
     }).sortable({
      items: "li",
      sort: function() {
        $( this ).removeClass("ui-state-default");
      }
   });

   //remove book from list
   $("#droppable li span").click(function() {
      $('#draggable').append($( this ).parent())
      $.ajax({
	    data: $( this ).parent().attr('id'),
	    type: 'POST',
	    url: '/ajax_del_position/'
      });
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
	//console.log(order);
	$.ajax({
	    data: order,
	    type: 'POST',
	    url: '/ajax_sort/',
	    success: function(res){
	      console.log(res);
              //json=JSON.parse(res);
	    }
	});
       }
   });

});
