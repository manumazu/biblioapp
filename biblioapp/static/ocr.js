$(document).ready(function() {

$('#start-ocr').on('click', function() {
    var elements = [];
    $(':checkbox:checked').each(function(i){
          //elements[i] = $(this).val();
          elements.push('img[]='+$(this).val());
    });
    params = elements.join('&');
    ajax_postOcr(params, this);
  });

});

function ajax_postOcr(elements, button) {
 /*row = element.split('_')[1];
 order = $(element).sortable('serialize');*/
 console.log(elements);
 $.ajax({
    data: elements,
    type: 'POST',
    url: '/ajax_ocr/',
    success: function(res){
      //window.location='/app/';
      $(button).text("Indexation started");
      $(button).addClass('btn-warning');
    },
    complete: function() {
      window.setTimeout(function() {
        $(button).text("Start indexation");
        $(button).removeClass('btn-warning');
      }, 1000);
    }
  });
}

