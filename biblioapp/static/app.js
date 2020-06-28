/* save positions methods */

   function ajax_postOrder(elements, button) {
       /*row = element.split('_')[1];
       order = $(element).sortable('serialize');*/
       console.log(elements);
       $.ajax({
		    data: elements,
		    type: 'POST',
		    url: '/ajax_sort/',
		    success: function(res){
		      //for bookshelf : check if capacity is exceeded
		      if(maxColsShelf !== undefined && maxColsShelf > 0) {
		      	updateBookshelf(res);
		      }
		      //window.location='/app/';
		      $(button).text("Changes saved");
		      $(button).addClass('btn-success');
		    },
		    complete: function() {
		    	window.setTimeout(function() {$(button).hide()}, 1000);
		    }
	    });
   }

  function ajax_supprItem(elem) {
      $('#draggable').append(elem.parent());
      $.ajax({
	    data: elem.parent().attr('id'),
	    type: 'POST',
	    url: '/ajax_del_position/',
	    success: function(res){
	      //for bookshelf : update values
	      if(maxColsShelf !== undefined && maxColsShelf > 0) {
	      	updateBookshelf(res);
	      }
		}
      });
      $('#draggable li').draggable({scope: "d1"}); //set list draggable again
  }


/* color editor methods */

  function getColor() {
    // returns a string of red, green, blue values
    var color = [];       
    color.push($('#red').val());
    color.push($('#green').val());
    color.push($('#blue').val());
    return color.join(',');
	}

	function updatePreview() {
	    var c = getColor();
	    $('#rgbText').text("Color is rgb(" + c  + ")");
	    $('#previewColor').css('backgroundColor','rgb(' + c + ')');
	}

	function colorEditor() {
	    $("#colorEditor").modal();
	    updatePreview();
	    $('input[type=range]').on('input', function () {
	        updatePreview();
	    });	    
	}