$(document).ready(function() {

$('#start-ocr').on('click', async function() {
    var elements = [];
    var numshelf = $('#numshelf').val();
    $(':checkbox:checked').each(function(){
          //elements[i] = $(this).val();
          elements.push('img[]='+$(this).val());
    });
    params = elements.join('&');
    params += '&numshelf='+numshelf;
    await ajax_postOcr(params, this);
  });

});

function waitingText(button, seconds) {
  var str = ".";
  if(!seconds)
    clearTimeout();
  else {
    for(let i=0; i<seconds; i++) {
      var timeoutID = window.setTimeout(function(){
          str+=".";
          //console.log(str);
          $(button).text("Indexation in process "+str);
      }, i * 1000);
    }
    console.log(timeoutID);
    return timeoutID;
  }
}

async function ajax_postOcr(images, button) {
 /*row = element.split('_')[1];
 order = $(element).sortable('serialize');*/
 console.log(images);
 $(button).text("Indexation in process ...");
 //const timeoutID = waitingText(button, 20);
 $(button).removeClass('btn-danger');
 $(button).addClass('btn-warning');
 return new Promise((resolve, reject) => {
   $.ajax({
      data: images,
      type: 'POST',
      url: '/api/ajax_ocr/',
      complete: function(res) {
        //console.log(res.responseText);
        var result=$.parseJSON(res.responseText);
        if(result.success == true) {
          //waitingText(button, 0);
          //clearTimeout(timeoutID);
          $(button).text("Start indexation");
          $(button).removeClass('btn-warning');
          //parse response and search by title
          console.log("ocr books found:", result.ocr_nb_books);
          displayOcrResult(result.response['found'], 'ocrResultFound');
          displayOcrResult(result.response['notfound'], 'ocrResultNotFound');
        }
        else {
          $(button).text("Indexation Error");
          $(button).removeClass('btn-warning');
          $(button).addClass('btn-danger');
        }
      }
    });
  })
}

function displayOcrResult(books, destination) {
  $('#'+destination+' ul').empty();
  //display book list 
  if(books.length) {
    $('#'+destination).show();
    for(let i = 0; i < books.length; i++) {
      //console.log(books[i])
      $("#"+destination+" ul").append('<li>'+books[i]['title']+', '+books[i]['author']+'</li>');
    }
  }
}


