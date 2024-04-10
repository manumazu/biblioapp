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
              let index = (j+1)
              let result = await ajax_indexBook(books[j], index, numshelf)
              //console.log(result)
              $('#ocrResultFound_' + ocr.img_num + ' ul').append(result);
              // disable list excepted first or already in shelf
              hasPosition = $('#book_' + index).hasClass('list-group-item-success');
              /*if(index > 1 && !hasPosition) {
                $('#book_' + index).addClass('disabled');
              }*/
              // force forms created not being submited
              $('form').on('submit', function(e){
                e.preventDefault();
              });          
            }
            //display ocr analyse total found
            console.log("ocr books found:", ocr.ocr_nb_books);           
          }
          else {
            $('#ocrResult').append('<div class="error"><hr><h2>OCR error for image ' + filename + '</h2><p>' + ocr.response + '</p></div>');
          }
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
async function ajax_indexBook(ocr, index, numshelf) {
  var elem = [];
  //console.log(ocr)
  elem.push('title='+ocr.title)
  elem.push('author='+ocr.author)
  elem.push('editor='+ocr.editor)
  elem.push('numbook='+index)
  elem.push('numshelf='+numshelf)
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

function enableForm(index) {
  //console.log(index);
  $('#book_' + index).removeClass('disabled');
}

// when the book can not be found
function doNotIndex(form_id) {
  $('#' + form_id).addClass('disabled');
  const index = form_id.split('_');
  enableForm(parseInt(index[1])+1)
}

//index book position using api
async function saveBook(form_id, numshelf) {
  const reference = $('#' + form_id + ' > form > input[name=reference]').val()
  const title = $('#' + form_id + ' > form > input[name=title]').val()
  const index = form_id.split('_');
  // save book + location 
  const data = await ajax_saveBook(reference, numshelf);
  //console.log(data);
  if(data['result'] == 'error') {
      $('#' + form_id).addClass('list-group-item-danger');
  }                         
  if(data['result'] == 'success' && data['address'] != undefined) {
      $('#' + form_id).addClass('list-group-item-success');
  }
  //display new posiion in shelf  
  if(typeof data['message'] != undefined){
    const message = index[1] + '- "' + title + '": ' + data['message'];
    $('#' + form_id).html(message);
    //enable next from
    enableForm(parseInt(index[1])+1)
  }
}

async function ajax_saveBook(reference, numshelf) {
  const params = 'numshelf='+numshelf+'&ref='+reference+'&save_bookapi=googleapis&forcePosition=true&token=ocr';
  return $.ajax({
    data: params, 
    url: '/api/bookreferencer/', 
    complete: function(res) {
      return res.responseText;
    }
  })
}

// search book and return results
async function searchBook(form_id) {
  const title = $('#' + form_id + ' > form > input[name=intitle]').val()
  const index = form_id.split('_');
  const result = await ajax_searchBook(title, index[1]);
  //console.log(result)
  $('#'+form_id).replaceWith(result);
  // force forms created not being submited
  $('form').on('submit', function(e){
    e.preventDefault();
  });  
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



