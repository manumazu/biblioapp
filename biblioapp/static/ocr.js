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
      statusCode: {
        500: function(res) {
          $('#ocrResult').append('<div class="error"><hr><h2>Server Error during process</h2><p>The Server returned an error.</p></div>');
          console.log('Error 500', res);
          clearInterval(timer);
        },
        502: function(res) {
          $('#ocrResult').append('<div class="error"><hr><h2>Timeout Error during process</h2><p>The Server returned an error.</p></div>');
          console.log('Error 502', res);
          clearInterval(timer);
        }
      },
      complete: async function(res) {
        //console.log(res.responseText);
        var result=$.parseJSON(res.responseText);
        clearInterval(timer);
        $(button).text("Start indexation");
        $(button).removeClass('btn-warning');
        //display ocr results for each image checked  
        for(let i=0; i<result.length; i++) 
        {
          if(result[i].success == true) {
            // use search book api for each ocr result
            var books = result[i].response;

            $('#ocrResult').append('<div id="ocrResultFound"><hr><h2>Books found for image ' + (i+1) + '</h2><ul></ul></div>');
            $('#ocrResult').append('<div id="ocrResultNotFound"><hr><h2>Books not found for image ' + (i+1) + '</h2><ul></ul></div>');
            $('#ocrResultFound').hide();
            $('#ocrResultNotFound').hide();

            for(let j = 0; j<books.length; j++) 
            {
              let result = await searchBook(books[j])
              //console.log(result)
              //parse search and display response
              if(result['found'].length > 0) {
                displayOcrResult(result['found'], 'ocrResultFound');
              }
              if(result['notfound'].length > 0) {
                displayOcrResult(result['notfound'], 'ocrResultNotFound');
              }          
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
  //$('#'+destination+' ul').empty();
  //display book list 
  if(books.length) {
    $('#'+destination).show();
    for(let i = 0; i < books.length; i++) {
      //console.log(books[i])
      $("#"+destination+" ul").append('<li>'+books[i]['title']+', '+books[i]['author']+'</li>');
    }
  }
}

// request for search api using ocr result
async function searchBook(ocr) {
  var elem = [];
  //console.log(ocr)
  elem.push('title='+ocr.title)
  elem.push('author='+ocr.author)
  elem.push('editor='+ocr.editor)
  params = elem.join('&');
 return $.ajax({
    data: params,
    type: 'POST',
    url: '/api/ajax_bookindexer/',
    complete: function(res) {
      //console.log(res.responseText)
      return res.responseText;
    }
  })
}

