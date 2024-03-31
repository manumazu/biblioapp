$(document).ready(function() {

$('#start-ocr').on('click', function() {
    $(this).text("Indexation in process");
    $(this).addClass('btn-warning');
    $('#ocrResult').empty();

    const timer = waitingButton(this, 20);
    var numshelf = $('#numshelf').val();
    var button = this;
    
    $(':checkbox:checked').each(async function(){

        const filename = $(this).val();
        const img_num = filename.split('_');

        // prepare display results
        $('#ocrResult').append('<div id="ocrResultFound_' + img_num[0] + '"><hr><h2>Books found for image ' + filename + '</h2><ul></ul></div>');
        $('#ocrResult').append('<div id="ocrResultNotFound_' + img_num[0] + '"><hr><h2>Books not found for image ' + filename + '</h2><ul></ul></div>');
        $('#ocrResultFound_' + img_num[0]).hide();
        $('#ocrResultNotFound_' + img_num[0]).hide();       

        //start ocr
        const params = 'img='+filename+'&numshelf='+numshelf+'&img_num='+img_num[0];
        const ocr = await ajax_postOcr(params, timer);
        //console.log(ocr); 

        if(ocr.success == true) {

          // use search book api for each ocr result
          const books = ocr.response;
          for(let j = 0; j<books.length; j++) {

            let result = await searchBook(books[j], (j+1))
            console.log('order ', result['numbook'])

            //parse search and display response
            if(result['found'].length > 0) {
              let book = result['found'][0];
              $('#ocrResultFound_' + ocr.img_num).show();
              //let linkRef = '<a href=' + book['ref_url'] + '>' + book['title'] + '</a>';
              //$('#ocrResultFound_' + ocr.img_num + ' ul').append('<li>' + linkRef + ', '+book['author']+', order: ' + j + ' / ' + result.numbook + '</li>');
              $('#ocrResultFound_' + ocr.img_num + ' ul').append(book);
            }
            if(result['notfound'].length > 0) {
              let book = result['notfound'][0];
              $('#ocrResultNotFound_' + ocr.img_num).show();
              $('#ocrResultNotFound_' + ocr.img_num + ' ul').append('<li>'+book['title']+', '+book['author']+', order: ' + j + ' / ' + result.numbook + '</li>');
            }

          }
          //display ocr analyse total found
          console.log("ocr books found:", ocr.ocr_nb_books);           
        }
        else {
          $('#ocrResult').append('<div class="error"><hr><h2>OCR error for image ' + filename + '</h2><p>' + ocr.response + '</p></div>');
        }

        $(button).text("Start indexation");
        $(button).removeClass('btn-warning');
        clearInterval(timer);           
    });

  });
});

async function ajax_postOcr(params, timer) {

 console.log(params);

 return $.ajax({
    data: params,
    type: 'POST',
    url: '/api/ajax_ocr/',
    statusCode: {
      500: function(res) {
        $('#ocrResult').append('<div class="error"><hr><h2>Server Error during process</h2><p>The Server returned an error.</p></div>');
        console.log('Error 500', res);
        clearInterval(timer);
      },
      502: function(res) {
        $('#ocrResult').append('<div class="error"><hr><h2>Timeout Error during process</h2><p>The Server returned a timeout error.</p></div>');
        console.log('Error 502', res);
        clearInterval(timer);
      }
    },
    complete: async function(res) {
      return res.responseText;
    }
  });
}

// request for search api using ocr result
async function searchBook(ocr, index) {
  var elem = [];
  //console.log(ocr)
  elem.push('title='+ocr.title)
  elem.push('author='+ocr.author)
  elem.push('editor='+ocr.editor)
  elem.push('numbook='+index)
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

