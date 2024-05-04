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
          const img_num = filename.split('_')[0];
          const resultListId =  'ocrResultFound_' + img_num;

          // prepare display results
          const list_header = '<hr><h2>Analyze result for image ' + filename + '</h2><ul class="list-group" style="color:#000"></ul>';
          $('#ocrResult').append('<div id="' + resultListId + '">' + list_header + '</div>');
          $('#' + resultListId).hide();

          //start ocr
          const params = 'img='+filename+'&numshelf='+numshelf+'&img_num='+img_num;
          const ocr = await ajax_postOcr(params, timer);
          //console.log(ocr); 

          if(ocr.success == true) 
          {
            $('#' + resultListId).show();
            // use search book api for each ocr result
            const books = ocr.response;
            for(let j = 0; j<books.length; j++) 
            {
              let index = (j+1)
              let result = await ajax_indexBook(books[j], index, numshelf, ocr.img_num)
              //console.log(result)
              $('#' + resultListId + ' ul').append(result);
              
              // force forms created not being submited
              $('form').on('submit', function(e){
                e.preventDefault();
              });          
            }
            console.log("ocr books found:", ocr.ocr_nb_books);

            // reorder all books for indexed items in list
            postOrder(resultListId, numshelf, ocr.img_num);            

          }
          // display ocr error
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
async function ajax_indexBook(ocr, index, numshelf, img_num) {
  var elem = [];
  //console.log(ocr)
  elem.push('title='+ocr.title)
  elem.push('author='+ocr.author)
  elem.push('editor='+ocr.editor)
  elem.push('numbook='+index)
  elem.push('numshelf='+numshelf)
  elem.push('img_num='+img_num)
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

function enableForm(index) {
  //console.log(index);
  $('#book_' + index).removeClass('disabled');
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

function doNotIndex(form_id) {
  $('#' + form_id).addClass('disabled');
  const index = form_id.split('_');
  enableForm(parseInt(index[1])+1)
}

//index book position using api
async function saveBook(form_id, numbook, numshelf) {
  const reference = $('#' + form_id + " > form > input[name=reference]").val()
  const title = $('#' + form_id + " > form > input[name=title]").val()
  const author = $('#' + form_id + " > form > input[name='authors[]']").val()
  const index = form_id.split('_');
  const img_num = $('#' + form_id + " > form > input[name='source_img_num']").val()
  console.log('img_num', img_num)

  // save book
  const data = await ajax_saveBook(reference, numshelf, index);
  //console.log(data);

  if(data['result'] == 'error') {
      $('#' + form_id).addClass('list-group-item-danger');
  }                         
  if(data['result'] == 'success' && typeof data['book'] !== 'undefined') {
      $('#' + form_id).removeClass('list-group-item-warning');
      $('#' + form_id).addClass('list-group-item-success');     
      //udapte id of book as added
      const newId = 'indexed_' + data['book']['id_book']; 
      $('#' + form_id).attr('id', newId)     
      //get list of books ids by order : 
      const resultListId =  $('#' + newId).parent().parent().attr('id');

      // build request for sorting book's postion by order in shelf
      postOrder(resultListId, numshelf, img_num);
  }
}

async function ajax_saveBook(reference, numshelf, index) {
  let params = 'numshelf='+numshelf+'&ref='+reference+'&save_bookapi=googleapis&token=ocr'; //&forcePosition=true
  //for book already index, get info by id
  if(index[0] == 'book')
    params += '&id_book='+index[1]
  return $.ajax({
    data: params, 
    url: '/api/bookreferencer/', 
    complete: function(res) {
      return res.responseText;
    }
  })
}

// search book and return results
async function searchBook(form_id, numshelf) {
  const title = $('#' + form_id + ' > form > input[name=intitle]').val()
  const img_num = $('#' + form_id + " > form > input[name='source_img_num']").val()
  const index = form_id.split('_');
  const result = await ajax_searchBook(title, index[1], numshelf, img_num);
  //console.log(result)
  $('#'+form_id).replaceWith(result);
  // force forms created not being submited
  $('form').on('submit', function(e){
    e.preventDefault();
  });  
}

// request for search api
async function ajax_searchBook(title, index, numshelf, img_num) {
  var elem = [];
  const payload = {
    title: title,
    numbook: index,
    search_api: 'googleapis',
    search_origin: 'ocr',
    numshelf: numshelf,
    img_num: img_num
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

// retrieve indexed books id, reorder LEDs position, update order in list
async function postOrder(resultListId, numshelf, img_num) {
  //build request for sorting book's postion by order in shelf
  let reqStr = "row="+numshelf+"&source_img_num="+img_num
  let cpt = 0;
  $('#' + resultListId + ' > ul > li').each(function(){ 
    
    const listId = $(this).attr('id');
    
    //increase interval for books not found or not in position index
    if(listId.indexOf('newbook') == 0 || listId.indexOf('book') == 0) {
      cpt++;
    }

    if(listId.indexOf('indexed') == 0) {
      const Id = listId.split('_');
      if(cpt>0)
        reqStr += '&book[]=empty_' + cpt; 
      reqStr += '&book[]=' + Id[1];
      cpt=0;
    }
    
  })

  // update order for books as found by ocr
  const newBookOrder = await ajax_postOrder(reqStr);
  // display info for new postion
  for (let i=0; i < newBookOrder.length; i++) {
    // update content book form content
    const newId = 'indexed_' + newBookOrder[i]['book'];      
    const msg = '(position n°' + newBookOrder[i]['position'] + ' and LED n°' + newBookOrder[i]['led_column'] + ')';
    $('#' + newId + ' > form > span').html(msg);
    //hide form buttons
    $('#' + newId + ' > form > .btn').each(function(){
      $(this).hide();
    })
    //console.log(newBookOrder[i]); 
  }
}

async function ajax_postOrder(elements) {
   console.log(elements);
   return $.ajax({
    data: elements,
    type: 'POST',
    url: '/ajax_sort/',
    complete: function(res) {
      return res.responseText;
    }
  });
}

