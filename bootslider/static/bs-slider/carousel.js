var animationClass, slideSelect;

function lazyLoadSrc(e)
{
    const index = (e.to + 1) % $('.carousel .carousel-item').length;
    const slideTarget = $(slideSelect + index);
    const image = slideTarget.find('img').first();
    console.debug("Requested lazy load on " + slideTarget.attr('id') + " img.src="+ image.attr('src') + "img.data-src=" + image.data('src'));

    if (image.attr('src'))
    {
        console.debug(slideTarget.attr('id') + " was preloaded");
    }
    else
    {
        // console.debug("bs.slide " + slideTarget.attr('id') + " " + image.data('src') + " from " + e.from);
        image.attr('src', image.data('src'));
        image.removeAttr('data-src');
    };

}

$(function()
{
    $('.carousel.lazy').bind('slide.bs.carousel', lazyLoadSrc);
});

$(document).ready(function()
{
    const el = $('.carousel .carousel-item').first();
    const preloadSecond = $('.carousel .carousel-item').eq(1);

    const sliderEl = $('.carousel').first();
    animationClass =  sliderEl.data('animationClass');
    slideSelect = "#" + sliderEl.data('slideSelect');

    el.show();

    console.debug(preloadSecond.attr('id'));
    setTimeout(function(){el.addClass(animationClass);}, 700);
    if (preloadSecond){ lazyLoadSrc({'relatedTarget': "#"+preloadSecond.attr('id'), 'to': 0, 'from': 0}) }
});
