$(document).ready(function(){
    $('.slider').bxSlider({
        mode: 'vertical',
        controls: false,
        touchEnabled: true,
        auto: true,
        randomStart: true,
        infiniteLoop: true,
        auto: true,
        speed: 1500,
        slideWidth: 822,
        minSlides: 1,
        slideMargin: 0,
        responsive: true,
        preloadImages: 'visible',
        // controls: true,
        onSliderLoad: function() {
            $('.posters-level1-body').css('opacity', '1');
            $('.posters-level1-body').css('height', 'auto');
        }
    });
});