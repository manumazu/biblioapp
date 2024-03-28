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
        //display ocr results for each image checked  
        for(let i=0; i<result.length; i++) 
        {
          if(result[i].success == true) {
            // use search book api for each ocr result
            var books = result[i].response;

            $('#ocrResult').append('<div id="ocrResultFound_' + i + '"><hr><h2>Books found for image ' + (i+1) + '</h2><ul></ul></div>');
            $('#ocrResult').append('<div id="ocrResultNotFound_' + i + '"><hr><h2>Books not found for image ' + (i+1) + '</h2><ul></ul></div>');
            $('#ocrResultFound_' + i).hide();
            $('#ocrResultNotFound_' + i).hide();

            for(let j = 0; j<books.length; j++) 
            {
              let result = await searchBook(books[j])
              //console.log(result)
              //parse search and display response
              if(result['found'].length > 0) {
                let book = result['found'][0];
                $('#ocrResultFound_' + i).show();
                $('#ocrResultFound_' + i + ' ul').append('<li>'+book['title']+', '+book['author']+'</li>');
              }
              if(result['notfound'].length > 0) {
                let book = result['notfound'][0];
                $('#ocrResultNotFound_' + i).show();
                $('#ocrResultNotFound_' + i + ' ul').append('<li>'+book['title']+', '+book['author']+'</li>');
              }          
            }
            //display ocr analyse total found
            console.log("ocr books found:", result[i].ocr_nb_books);
          }
          else {
            $('#ocrResult').append('<div class="error"><hr><h2>OCR error for image ' + (i+1) + '</h2><p>' + result[i].response + '</p></div>');
          }
        }
        $(button).text("Start indexation");
        $(button).removeClass('btn-warning');        
        clearInterval(timer);
      }
    });
  })
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

