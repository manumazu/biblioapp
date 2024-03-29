$(document).ready(function() {

$('#start-ocr').on('click', function() {
    $(this).text("Indexation in process");
    $(this).removeClass('btn-danger');
    $(this).addClass('btn-warning');

    $('#ocrResult').empty();
    const timer = waitingButton(this, 20);
    var numshelf = $('#numshelf').val();
    var i = 0;
    var button = this;
    
    $(':checkbox:checked').each(async function(){
        //start ocr
        i++;
        let params = 'img='+$(this).val()+'&numshelf='+numshelf+'&img_num='+i;
        let ocr = await ajax_postOcr(params, timer);
        console.log(ocr);

        //var ocr = $.parseJSON(res.responseText);
        var img_num = ocr.img_num;       

        if(ocr.success == true) {
          
          // prepare display results
          $('#ocrResult').append('<div id="ocrResultFound_' + img_num + '"><hr><h2>Books found for image ' + img_num + '</h2><ul></ul></div>');
          $('#ocrResult').append('<div id="ocrResultNotFound_' + img_num + '"><hr><h2>Books not found for image ' + img_num + '</h2><ul></ul></div>');
          $('#ocrResultFound_' + img_num).hide();
          $('#ocrResultNotFound_' + img_num).hide();

          // use search book api for each ocr result
          var books = ocr.response;
          for(let j = 0; j<books.length; j++) {

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
          console.log("ocr books found:", ocr.ocr_nb_books);           
        }
        else {
          $('#ocrResult').append('<div class="error"><hr><h2>OCR error for image ' + img_num + '</h2><p>' + ocr.response + '</p></div>');
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
        $('#ocrResult').append('<div class="error"><hr><h2>Timeout Error during process</h2><p>The Server returned an error.</p></div>');
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

