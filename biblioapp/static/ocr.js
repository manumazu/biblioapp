$(document).ready(function() {

$('#start-ocr').on('click', function() {
    $(this).text("Indexation in process");
    $(this).removeClass('btn-danger');
    $(this).addClass('btn-warning');
    const timer = waitingButton(this, 20);
    var numshelf = $('#numshelf').val();
    var i = 0;
    var button = this;
    $(':checkbox:checked').each(async function(){
        i++;
        let params = 'img='+$(this).val()+'&numshelf='+numshelf+'&img_num='+i;
        await ajax_postOcr(params, timer, button);
    });
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

async function ajax_postOcr(image, timer, button) {
 /*row = element.split('_')[1];
 order = $(element).sortable('serialize');*/
 console.log(image);
 $('#ocrResult').empty();
 return new Promise((resolve, reject) => {
   $.ajax({
      data: image,
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
        var ocr_res = $.parseJSON(res.responseText);
        var img_num = ocr_res.img_num;       

        if(ocr_res.success == true) {
          // use search book api for each ocr result
          var books = ocr_res.response;
          $('#ocrResult').append('<div id="ocrResultFound_' + img_num + '"><hr><h2>Books found for image ' + img_num + '</h2><ul></ul></div>');
          $('#ocrResult').append('<div id="ocrResultNotFound_' + img_num + '"><hr><h2>Books not found for image ' + img_num + '</h2><ul></ul></div>');
          $('#ocrResultFound_' + img_num).hide();
          $('#ocrResultNotFound_' + img_num).hide();

          for(let j = 0; j<books.length; j++) 
          {
            let result = await searchBook(books[j])
            //console.log(result)
            //parse search and display response
            if(result['found'].length > 0) {
              let book = result['found'][0];
              $('#ocrResultFound_' + img_num).show();
              $('#ocrResultFound_' + img_num + ' ul').append('<li>'+book['title']+', '+book['author']+'</li>');
            }
            if(result['notfound'].length > 0) {
              let book = result['notfound'][0];
              $('#ocrResultNotFound_' + img_num).show();
              $('#ocrResultNotFound_' + img_num + ' ul').append('<li>'+book['title']+', '+book['author']+'</li>');
            }
          }
          //display ocr analyse total found
          console.log("ocr books found:", ocr_res.ocr_nb_books);           
        }
        else {
          $('#ocrResult').append('<div class="error"><hr><h2>OCR error for image ' + img_num + '</h2><p>' + ocr_res.response + '</p></div>');
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

