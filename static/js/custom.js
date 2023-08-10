(function($){
	// Preloader
	$(window).on("load", function(){
		$(".preloader").fadeOut();
	});
    $(document).ready(function(){
		// Sticky Navigation Bar
		$(window).scroll(function(){
			var scrollHeight = $(document).scrollTop();
			if(scrollHeight > 250){
				$('.navigation').addClass('navigation-fixed');
			}else{
				$('.navigation').removeClass('navigation-fixed');
			}
		});

        // Search Box
		var $showsearchbox = $(".search-icon i");
		var $togglesearchbox = $(".searchbox");
		$(document).on('click', function(e) {
			var clickID = e.target.id;
			if ((clickID !== 's')) {
				$togglesearchbox.removeClass('show');
			}
		});
		$showsearchbox.on('click', function(e) {
			e.stopPropagation();
		});
		$('.search-form').on('click', function(e) {
			e.stopPropagation();
		});
		$showsearchbox.on('click', function(e) {
			if (!$togglesearchbox.hasClass("show")) {
				$togglesearchbox.addClass('show');
				e.preventDefault();
			} else
				$togglesearchbox.removeClass('show');
			e.preventDefault();

			if (!$showsearchbox.hasClass("active"))
				$showsearchbox.addClass('active');
			else
				$showsearchbox.removeClass('active');
		});
		
		// Scroll To Top
		$('.totop').hide();
		$(window).on("scroll", function(){
			var scrollHeight = $(document).scrollTop();

			if(scrollHeight > 50){
				$('.header').addClass('nav-fixed');
			}else{
				$('.header').removeClass('nav-fixed');
			}
			// Scroll To Top Apearing
			if(scrollHeight > 150){
				$('.totop').fadeIn();
			}else{
				$('.totop').fadeOut();
			}
		});
		$(".totop a").click(function(event){
			$("html").animate({scrollTop:$("body").offset().top}, "1000");
			event.preventDefault();
		});
        
        // Mobile Menu
		$('.desktop-menu').meanmenu({
			meanMenuContainer	: '.mobile-menu',
			meanScreenWidth		: '991',
            meanMenuClose 		: '<i class="fas fa-times"></i>',
            removeElements      : '.col-lg-2',
            meanMenuOpen        : '<span></span><span></span><span></span>'
		});
		
		// Ticker Ingration
		$('.ticker').AcmeTicker({
			controls: {
			  prev		: $('.inews-ticker-prev'),
			  toggle	: $('.inews-ticker-pause'),
			  next		: $('.inews-ticker-next')
			},			
			speed		: 50,
			autoplay 	: 2000,
			type		: 'typewriter',
			pauseOnHover: false
		});

		// Post Block 1 Slider
		$('.block1-slider').owlCarousel({
			items				: 3,
			dots				: false,
			margin				: 10,
			loop				: true,
			nav					: true,
			responsive			: {
				992				: {
					navText		: ['<i class="fas fa-chevron-left"></i>', '<i class="fas fa-chevron-right"></i>'],
					items		: 3
				},
				768				: {
					items		: 2
				},
				0				: {
					items		: 1
				}
			}
		});

		// Gallery Slider
		$('.gallery-slider').owlCarousel({
			items				: 1,
			dots				: false,
			loop				: true,
			nav					: true,
			navText				: ['<i class="fas fa-chevron-left"></i>', '<i class="fas fa-chevron-right"></i>']
			
		});


    });
}(jQuery))