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

async function ajax_postOcr(elements, button) {
 /*row = element.split('_')[1];
 order = $(element).sortable('serialize');*/
 console.log(elements);
 $(button).text("Indexation in process ...");
 $(button).removeClass('btn-danger');
 $(button).addClass('btn-warning');
 return new Promise((resolve, reject) => {
   $.ajax({
      data: elements,
      type: 'POST',
      url: '/api/ajax_ocr/',
      complete: function(res) {
        //console.log(res.responseText);
        var json=$.parseJSON(res.responseText);
        for(let i = 0; i < json.length; i++) {
          result = json[i];
          //console.log(result);
          if(result.success == true) {
            $(button).text("Start indexation");
            $(button).removeClass('btn-warning');
            //parse response and search by title
            var books = result.response;
            for(let i = 0; i < books.length; i++) {
              searchBook(books[i])
            }
          }
          else {
            $(button).text("Indexation Error");
            $(button).removeClass('btn-warning');
            $(button).addClass('btn-danger');
          }
        }
      }
    });
  })
}

function searchBook(book) {
  var elem = [];
  elem.push('intitle='+book.title)
  elem.push('inauthor='+book.authors)
  elem.push('inpublisher='+book.editor)
  params = elem.join('&');
  params += '&is_ocr=1';
  //params = JSON.stringify(elem);
  return new Promise((resolve, reject) => {
   $.ajax({
      data: params,
      type: 'POST',
      url: '/api/booksearch/',
      complete: function(res) {
        console.log(res.responseText)
      }
    })
  })
}

