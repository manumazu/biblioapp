   function ajax_postOrder(elements,row) {
       /*row = element.split('_')[1];
       order = $(element).sortable('serialize');*/
       $.ajax({
		    data: elements+'&row='+row,
		    type: 'POST',
		    url: '/ajax_sort/',
		    success: function(res){
		      //json=JSON.parse(res.responseText);
		      console.log(res);
		      //window.location='/app/';
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