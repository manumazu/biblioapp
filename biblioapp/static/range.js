$(document).ready(function() {

   var selectedClass = 'ui-state-default';
   var i = 0;

   //remove book from list
   $("#droppable li span, #draggable li span").click(function() {//
      ajax_supprItem($( this ));
   });

   $("#droppable").droppable({
      scope: "d1",
      activeClass: "ui-state-default",
      hoverClass: "ui-state-hover",
      accept: '#draggable li',
      drop: function( event, ui ) {
        i++;
	ui.draggable.remove();
	ui.draggable.detach().css({top: 0,left: 0}).appendTo($(this));

        var order = $('#droppable').sortable('serialize'); 
	ajax_postOrder(order);
	
	//specific event for deleting dropped item
        ui.draggable.find('span').click(function() {
           ajax_supprItem($( this ));
	});
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
        ajax_postOrder(order);
       }
   });

   function ajax_postOrder(order) {
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

  function ajax_supprItem(elem) {
      $('#draggable').append(elem.parent());
      $.ajax({
	    data: elem.parent().attr('id'),
	    type: 'POST',
	    url: '/ajax_del_position/'
      });
  }
});
