$(document).ready(function() {

    $('#colorEditor-save').on('click', function() {

        if($('#red').val() != 0 || $('#green').val() != 0 || $('#blue').val() != 0 ) 
        {
            $.ajax({
                data: 'red='+$('#red').val()+'&green='+$('#green').val()+'&blue='+$('#blue').val(),
                type: 'POST',
                url: '/ajax_tag_color/'+$('#tag_id').val(),
                success: function(res){
                    if(res==true)
                        $('#rgbText').text("Color saved");
                    var c = getColor();
                    $('.badge').css("background-color", "rgb("+c+")");
                }
            });
        }
        
    });

});
