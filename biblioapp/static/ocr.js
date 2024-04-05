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
          const list_header = '<hr><h2>Analyze result for image ' + filename + '</h2><ul class="list-group" style="color:#000"></ul>';
          $('#ocrResult').append('<div id="ocrResultFound_' + img_num[0] + '">' + list_header + '</div>');
          $('#ocrResultFound_' + img_num[0]).hide();

          //start ocr
          const params = 'img='+filename+'&numshelf='+numshelf+'&img_num='+img_num[0];
          const ocr = await ajax_postOcr(params, timer);
          //console.log(ocr); 

          if(ocr.success == true) 
          {
            $('#ocrResultFound_' + ocr.img_num).show();
            // use search book api for each ocr result
            const books = ocr.response;
            for(let j = 0; j<books.length; j++) 
            {
              let result = await ajax_indexBook(books[j], (j+1))
              //console.log(result)
              $('#ocrResultFound_' + ocr.img_num + ' ul').append(result);
            }
            //display ocr analyse total found
            console.log("ocr books found:", ocr.ocr_nb_books);           
          }
          else {
            $('#ocrResult').append('<div class="error"><hr><h2>OCR error for image ' + filename + '</h2><p>' + ocr.response + '</p></div>');
          }
          // force forms created not being submited
          $('form').on('submit', function(e){
            e.preventDefault();
          });
          // set button in normal mode
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
    complete: function(res) {
      return res.responseText;
    }
  });
}

// request for search api using ocr result
async function ajax_indexBook(ocr, index) {
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

//index book position using api
function saveBook(form_id) {
  const reference = $('#' + form_id + ' > form > input[name=reference]').val()
  const elem = [];
  elem.push('ref='+reference)
  elem.push('save_bookapi=googleapis')
  params = elem.join('&');
  console.log(params);
}

// search book and return results
async function searchBook(form_id) {
  const title = $('#' + form_id + ' > form > input[name=intitle]').val()
  const index = form_id.split('_');
  const result = await ajax_searchBook(title, index[1])
  //console.log(result)
  $('#'+form_id).replaceWith(result);
}

// request for search api
async function ajax_searchBook(title, index) {
  var elem = [];
  const payload = {
    title: title,
    numbook: index,
    search_api: 'googleapis',
    search_origin: 'ocr'
  };  
  return $.ajax({
    data: JSON.stringify(payload), 
    type: 'POST',
    contentType: "application/json",
    url: '/api/booksearch/', 
    complete: function(res) {
      return res.responseText;
    }
  })
}



