$(document).ready(function(){
    $('.slider').bxSlider({
        mode: 'vertical',
        speed: 2000,
        slideMargin: 0,
        randomStart: true,
        infiniteLoop: true,
        responsive: true,
        preloadImages: 'visible',
        touchEnabled: true,
        preventDefaultSwipeX: true,
        preventDefaultSwipeY: true,
        pager: true,
        controls: false,
        auto: true,
        autoStart: true,
        autoDirection: 'next',
        autoHover: true,
        minSlides: 1,
        slideWidth: 822,
        onSliderLoad: function() {
            $('.poster-big-horizontal-body').css({
                'opacity': '1',
                'height': 'auto'
            });
        }
    });
});