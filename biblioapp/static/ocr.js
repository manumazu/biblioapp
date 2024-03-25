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

function waitingButton(button, seconds) {
    var str = ".";
    function run() {
      str+=".";
      $(button).text("Indexation in process "+str);
      if(str.length > 20)
        str = '.';
    }
    return setInterval(run, 500);
}

async function ajax_postOcr(images, button) {
 /*row = element.split('_')[1];
 order = $(element).sortable('serialize');*/
 console.log(images);
 $(button).text("Indexation in process");
 const timer = waitingButton(button, 20);
 $(button).removeClass('btn-danger');
 $(button).addClass('btn-warning');
 $('#ocrResult').empty();
 return new Promise((resolve, reject) => {
   $.ajax({
      data: images,
      type: 'POST',
      url: '/api/ajax_ocr/',
      complete: function(res) {
        //console.log(res.responseText);
        var result=$.parseJSON(res.responseText);
        clearInterval(timer);
        $(button).text("Start indexation");
        $(button).removeClass('btn-warning');
        //display results      
        for(let i=0; i<result.length; i++) 
        {
          if(result[i].success == true) {
            //parse search response
            if(result[i].response['found'].length > 0) {
              $('#ocrResult').append('<div id="ocrResultFound"><hr><h2>Books found for image ' + (i+1) + '</h2><ul></ul></div>');
              displayOcrResult(result[i].response['found'], 'ocrResultFound');
            }
            if(result[i].response['notfound'].length > 0) {
              $('#ocrResult').append('<div id="ocrResultNotFound"><hr><h2>Books not found for image ' + (i+1) + '</h2><ul></ul></div>');
              displayOcrResult(result[i].response['notfound'], 'ocrResultNotFound');
            }
            //display ocr analyse total found
            console.log("ocr books found:", result[i].ocr_nb_books);
          }
          else {
            $('#ocrResult').append('<div class="error"><hr><h2>OCR error for image ' + (i+1) + '</h2><p>' + result[i].response + '</p></div>');
          }
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


