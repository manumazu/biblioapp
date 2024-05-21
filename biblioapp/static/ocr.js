$(document).ready(function() {

  $('#start-ocr').on('click', function() {
      $(this).text("Analyze in process");
      $(this).addClass('btn-warning');
      $('#ocrResult').empty();

      const timer = waitingButton(this, 20);
      var numshelf = $('#numshelf').val();
      var button = this;
      let autoindex = 0;
      if($('#autoindex').is(':checked')){
        autoindex = 1;
      }
      let params = ''; 

      $('input[name=shelf-pictures]:checked').each(async function(){

          // set params for selected images
          const filename = $(this).val();
          const img_num = filename.split('_')[0];
          const resultListId =  'ocrResultFound_' + img_num;

          // prepare display results
          const list_header = '<hr><h2>Analyze result for image ' + filename + '</h2><ul class="list-group" style="color:#000"></ul>';
          $('#ocrResult').append('<div id="' + resultListId + '">' + list_header + '</div>');
          $('#' + resultListId).hide();

          //start ocr
          params = 'img='+filename+'&numshelf='+numshelf+'&img_num='+img_num+'&autoindex='+autoindex;
          const ocr = await ajax_postOcr(params, timer);
          //console.log(ocr); 

          if(ocr.success == true) 
          {
            $('#' + resultListId).show();
            // use search book api for each ocr result
            const books = ocr.response;
            let previousBook = null;
            for(let j = 0; j<books.length; j++) 
            {
              let index = (j+1)
              // need the previous indexed book id in list for finding next position
              if(j>0) {
                previousBook = $('#' + resultListId + ' ul li')[j-1];
                previousBook = $(previousBook).attr('id')
              }              
              console.log('previousIndex:', previousBook)
              let result = await ajax_indexBook(books[j], index, numshelf, ocr.img_num, autoindex, previousBook)
              //console.log(result)
              const resultList = $('#' + resultListId + ' ul') 
              resultList.append(result);
              //const currentIndex = $(result)[2];//.attr('id');
              //const previousIndex = $(currentIndex).parent().parent().attr('id');

              // force forms created not being submited
              $('form').on('submit', function(e){
                e.preventDefault();
              });          
            }
            console.log("ocr books found:", ocr.ocr_nb_books);

            // automatic reorder all books for indexed items in list
            if(autoindex) {
              postOrder(resultListId, numshelf, ocr.img_num);  
            }
            else {
              //button save position at the end of book list
              const button = `<button class="btn btn-success" onClick="postOrder('${resultListId}', ${numshelf}, ${ocr.img_num})" \
              style="display:block; margin:10px auto">Save all positions</button>`
              $('#' + resultListId).append(button)
            }

          }
          // display ocr error
          else {
            $('#ocrResult').append('<div class="error"><hr><h2>OCR error for image ' + filename + '</h2><p>' + ocr.response + '</p></div>');
          }
          // set button in normal mode
          $(button).text("Start analyze");
          $(button).removeClass('btn-warning');
          clearInterval(timer);          
    });

    // verif params
    if(params == '') {
      alert('you should check image');
      $(button).text("Start analyze");
      $(button).removeClass('btn-warning');
      clearInterval(timer);   
      return false;
    }

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
async function ajax_indexBook(ocr, index, numshelf, img_num, autoindex, previousBook) {
  var elem = [];
  //console.log(ocr)
  if('id_book' in ocr)
    elem.push('id_book='+ocr.id_book)
  elem.push('title='+ocr.title)
  elem.push('author='+ocr.author)
  elem.push('editor='+ocr.editor)
  elem.push('numbook='+index)
  elem.push('numshelf='+numshelf)
  elem.push('img_num='+img_num)
  elem.push('autoindex='+autoindex)
  // if(previousIndex != null)
  //   elem.push('previousbook='+previousBook)
  params = elem.join('&');
  //console.log(params)
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
      $(button).text("Analyze in process "+str);
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
  const editor = $('#' + form_id + " > form > input[name=editor]").val()
  const book_id = $('#' + form_id + " > form > input[name=id]").val()
  const index = form_id.split('_');
  const img_num = $('#' + form_id + " > form > input[name='source_img_num']").val()
  const resultListId =  $('#' + form_id).parent().parent().attr('id');
  
  // save book
  const book = {'title':title, 'author':author, 'numbook':numbook, 'numshelf':numshelf, 'img_num':img_num, 'id_book':book_id}
  let result = await ajax_indexBook(book, numbook, numshelf, img_num, 'save_book')//, previousBook)
  //console.log(result)
  $('#' + form_id).replaceWith(result);

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
  if($('#reset_positions').is(':checked')){
      reqStr += '&reset_positions=1';
  }      
  let cpt = 0;
  $('#' + resultListId + ' > ul > li').each(function(){ 
    
    const listId = $(this).attr('id');
    
    //increase position interval for books not indexed
    if(listId.indexOf('newbook') == 0) {
      cpt++;
    }

    if(listId.indexOf('indexed') == 0 || listId.indexOf('book') == 0) {
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
    // update class if needed
    if($('#' + newId).hasClass('list-group-item-success') == false) {
      $('#' + newId).addClass('list-group-item-success');
    }
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

function deleteImage(img_name, numshelf) {
  const test = confirm(img_name + ' will be destroyed. Are you sure ?');
  if(test) {
    $.ajax({
      data: 'delete=1&numshelf='+numshelf+'&filename='+img_name,
      type: 'POST',
      url: window.location.pathname,
      success: function(res) {
        window.location = window.location.href    
      }
    });
  }
}

