function initSlide(){
	var $container = $('.pos_center_con');
	var oldTimer = $container.data('slideTimer');
	if (oldTimer) {
		clearInterval(oldTimer);
	}
	$container.off('.slide');
	$('.prev').off('.slide');
	$('.next').off('.slide');
	$('.points').empty().off('.slide');
	$('.slide li').stop(true, true).css({'opacity':1});

	var $slides = $('.slide li');
	var len = $slides.length;
	if (len === 0) {
		return;
	}
	var nowli = 0;
	var prevli = 0;
	var $prev = $('.prev');
	var $next = $('.next');
	var timer = null;
	$slides.not(':first').css({'opacity':0});

	$slides.each(function(index, el) {
		var $li = $('<li>');
		if(index==0)
		{
			$li.addClass('active');
		}
		$li.appendTo($('.points'));
	});

	var $points = $('.points li');
	if (len > 1) {
		timer = setInterval(autoplay,4000);
		$container.data('slideTimer', timer);
	}

	$container.on('mouseenter.slide', function() {
		clearInterval(timer);
	});
	
	$container.on('mouseleave.slide', function() {
		if (len > 1) {
			timer = setInterval(autoplay,4000);
			$container.data('slideTimer', timer);
		}
	});

	function autoplay(){
		nowli++;
		move();
		$points.eq(nowli).addClass('active').siblings().removeClass('active');
	};

	$points.on('click.slide', function() {
		nowli = $(this).index();		
		$(this).addClass('active').siblings().removeClass('active');
		move();
	});
	$prev.on('click.slide', function() {
		nowli--;
		move();
		$points.eq(nowli).addClass('active').siblings().removeClass('active');
	});	
	$next.on('click.slide', function() {
		nowli++;
		move();
		$points.eq(nowli).addClass('active').siblings().removeClass('active');

	});

	function move(){
		if(nowli==prevli)
		{
			return;
		}

		if(nowli<0)
		{
			nowli=len-1;
			prevli = 0
			$slides.eq(nowli).animate({'opacity':1},800);
			$slides.eq(prevli).animate({'opacity':0},800);
			prevli=nowli;
			return;
		}

		if(nowli>len-1)
		{
			nowli = 0;
			prevli = len-1;
			$slides.eq(nowli).animate({'opacity':1},800);
			$slides.eq(prevli).animate({'opacity':0},800);
			prevli=nowli;
			return;
		}

		if(prevli<nowli)
		{
			$slides.eq(nowli).animate({'opacity':1},800);
			$slides.eq(prevli).animate({'opacity':0},800);
			prevli=nowli;			
		}
		else
		{			
			$slides.eq(nowli).animate({'opacity':1},800);
			$slides.eq(prevli).animate({'opacity':0},800);
			prevli=nowli;		
		}
	}
}
