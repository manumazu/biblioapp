$(document).ready(function() {

   var selectedClass = 'ui-state-default';//, droppableElements=['#droppable_1', '#droppable_2', '#droppable_3'];
   var i = 0;
   var order = [];

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
 
		ajax_postOrder(element);

		//specific event for deleting dropped item
		ui.draggable.find('span').one('click', function() {
		   ajax_supprItem($( this ));
		});
	     }
	     }).sortable({
	      items: "li",
	      sort: function() {
		$( this ).removeClass("ui-state-default");
	      }
	   });

	   $(element).delay( 1000 ).sortable({
		update: function(e, ui) {
		// POST to server using $.ajax for given row
		ajax_postOrder(element);
	       }
	   });

	   //remove book from list
	   $(element+" li span").one('click', function() {
		ajax_supprItem($( this ));
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

   function ajax_postOrder(element) {
       row = element.split('_')[1];
       order = $(element).sortable('serialize');
       $.ajax({
	    data: order+'&row='+row,
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
	    url: '/ajax_del_position/',
      });
      $('#draggable li').draggable({scope: "d1"}); //set list draggable again
  }
});
