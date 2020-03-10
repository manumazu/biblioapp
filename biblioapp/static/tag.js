function getColor() {
    // returns a string of red, green, blue values
    var color = [];
    color.push($('#red').val());
    color.push($('#green').val());
    color.push($('#blue').val());
    return color.join(',');
}

function updatePreview() {
    var c = getColor();
    $('#rgbText').text("Color is rgb(" + c  + ")");
    $('#previewColor').css('backgroundColor','rgb(' + c + ')');
}

function colorEditor() {
    $("#colorEditor").modal();
}

$(document).ready(function() {

    updatePreview();
    $('input[type=range]').on('input', function () {
        updatePreview();
    });

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
                }
            });
        }
        
    });

});
