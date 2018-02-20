$(document).ready(function(e) {
    $('body').prepend('<span class="viewport" style="background: #FFF; border: 2px dotted #000; border-radius: 1rem; font-weight: bold; padding: 0.5rem; position: fixed; bottom: 0; right: 0; z-index: 100000;"></span>');
    showViewportSize();    
});
$(window).resize(function(e) {
    showViewportSize();
});

function showViewportSize() {
    var viewport  = ( $(window).width() + 17 ) + ' x ' + $(window).height();                  
    $('.viewport').text(viewport);

}
