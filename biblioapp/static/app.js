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
		      if(typeof maxColsShelf !== 'undefined') {
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

function getColor(from = null) {
	//parse color from form field
	if(from != null) {
		var rgb = $('#'+from).val();	
		if(rgb != 'undefined' && rgb != '') 
		{
			var colors = $('#'+from).val().split(",");
			$('#red').val(colors[0]);
			$('#green').val(colors[1]);
			$('#blue').val(colors[2]);
			return rgb;
		}
		else { //init with empty colors
			$('#red').val(0);
			$('#green').val(0);
			$('#blue').val(0);
			return '0,0,0';
		}
	}
	else {
		// returns a string of red, green, blue values
		var color = [];       
		color.push($('#red').val());
		color.push($('#green').val());
		color.push($('#blue').val());
		return color.join(',');
	}
}

function updatePreview(from = null) {
    var c = getColor(from);
    $('#rgbText').text("Color is rgb(" + c  + ")");
    $('#previewColor').css('backgroundColor','rgb(' + c + ')');
}

function colorEditor(dest = null) {
    $("#colorEditor").modal();
    updatePreview(dest);
    $('input[type=range]').on('input', function () {
        updatePreview();
    });
    if(dest !== null) {
    	$('#destination').val(dest);
    }	    
}

/*$('#videosPresentation .close').click(function(){
  $('.embedVideo').each(function(){
    $(this).stopVideo();
  });
});*/

//for service worker
if("serviceWorker" in navigator) {
	navigator.serviceWorker.register("/sw.js").then(function(e){
		console.log("App: Achievement unlocked.");
	}).catch(function(e){
		console.error("App: Crash for register",e);
	});
}