$(document).ready(function() {

$('#start-ocr').on('click', async function() {
    var elements = [];
    var numshelf = $('#numshelf').val();
    $(':checkbox:checked').each(function(i){
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
      url: '/ajax_ocr/',
      complete: function(res) {
        //console.log(res.responseText);
        var json=$.parseJSON(res.responseText);
        for(let i = 0; i < json.length; i++) {
          result = json[i];
          //console.log(result);
          if(result.success == true) {
            $(button).text("Start indexation");
            $(button).removeClass('btn-warning');
            console.log(result.response);
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

