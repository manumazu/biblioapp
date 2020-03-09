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
    $('#rgbText').text("color rgb(" + c  + ")");
    $('#previewColor').css('backgroundColor','rgb(' + c + ')');
}

$(document).ready(function() {

    $('input[type=range]').on('input', function () {
        updatePreview();
    });

});