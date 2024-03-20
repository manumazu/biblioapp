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

// search isbn, ref ... of ocr books with api 
function searchBook(search) {
  var elem = [];
  elem.push('intitle='+search.title)
  elem.push('inauthor='+search.authors)
  elem.push('inpublisher='+search.editor)
  params = elem.join('&');
  params += '&is_ocr=1';
  //params = JSON.stringify(elem);
  return new Promise((resolve, reject) => {
   $.ajax({
      data: params,
      type: 'POST',
      url: '/api/booksearch/',
      complete: function(res) {
        //console.log(res.responseText)
        var results = $.parseJSON(res.responseText);
        let first = 0;
        for(let i = 0; i < results.length; i++) {
          let result = results[i]
          let title = result.title
          let regex = new RegExp( search.title, 'gi' );
          let found = title.match(regex);
          //console.log(found)
          if(found && found.length > 0) {
            first++
            //take the first of the result list only
            if(first == 1) {
              console.log('-----FOUND-----')
              console.log('Author', result.author)
              console.log('Title', result.title)
              console.log('Ref', result.reference)
            }
          }
        }
        // manage ocr books not found    
        if(first == 0) {
          console.log('-----NOT FOUND !!-----')
          console.log('Author', search.authors)
          console.log('Title', search.title)
        }
      }
    })
  })
}

