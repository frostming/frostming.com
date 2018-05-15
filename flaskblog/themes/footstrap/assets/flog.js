var hasMobileUA = function () {
    var nav = window.navigator;
    var ua = nav.userAgent;
    var pa = /iPad|iPhone|Android|Opera Mini|BlackBerry|webOS|UCWEB|Blazer|PSP|IEMobile|Symbian/g;

    return pa.test(ua);
};
var isMobile = function () {
    return window.screen.width < 767 && this.hasMobileUA();
};
(-1 !== navigator.platform.indexOf("Win") || isMobile()) && (document.body.className = "win");
$(document).ready(function () {
    var headerHeight = $('.post-cover').outerHeight();
    $(window).on('scroll', function () {
        $('nav.navbar').toggleClass('has-bg', window.pageYOffset > headerHeight);
        $('nav.navbar').toggleClass('navbar-light', window.pageYOffset > headerHeight);
        $('nav.navbar').toggleClass('navbar-dark', window.pageYOffset < headerHeight);
        $('#totop').toggleClass('invisible', $(window).scrollTop() < $(window).height() * 0.8);
        $('#totop').toggleClass('visible', $(window).scrollTop() > $(window).height() * 0.8);
    });

    $('body').scrollspy({
        target: '.post-toc',
        offset: 200,
    });

    $('#totop').on('click', function () {
        $('html, body').animate({
            scrollTop: 0
        }, 1000, function () {
            $("#totop").removeClass("visible").addClass('invisible');
        });
    });
});

$(function () {
    var $pswp = $('.pswp');
    if ($pswp.length === 0) return;
    $pswp = $pswp[0];
    var currentLoad = 0;

    var getItems = function () {
        var items = [];
        $('figure img').each(function () {
            var src = $(this).attr('src'),
                width = this.naturalWidth,
                height = this.naturalHeight;

            var item = { src: src, w: width, h: height, el: this };
            var figcaption = $(this).find('+figcaption').first();
            if (figcaption.length !== 0) item.title = figcaption.html();
            items.push(item);
        });
        return items;
    };

    var bindEvent = function () {
        var items = getItems();
        $('figure img').each(function (i) {

            $(this).on('click', function (e) {
                e.preventDefault();

                var options = {
                    index: i,
                    getThumbBoundsFn: function (index) {
                        // See Options->getThumbBoundsFn section of docs for more info
                        var thumbnail = items[index].el,
                            pageYScroll = window.pageYOffset || document.documentElement.scrollTop,
                            rect = thumbnail.getBoundingClientRect();

                        return {
                            x: rect.left,
                            y: rect.top + pageYScroll,
                            w: rect.width
                        };
                    },
                };

                // Initialize PhotoSwipe
                var gallery = new PhotoSwipe($pswp, PhotoSwipeUI_Default, items, options);
                gallery.listen('gettingData', function (index, item) {
                    if (item.w < 1 || item.h < 1) { // unknown size
                        var img = new Image();
                        img.onload = function () { // will get size after load
                            item.w = this.width; // set image width
                            item.h = this.height; // set image height
                            gallery.invalidateCurrItems(); // reinit Items
                            gallery.updateSize(true); // reinit Items
                        };
                        img.src = item.src; // let's download image
                    }
                });
                gallery.init();
            });
        });
    };
    bindEvent();

});