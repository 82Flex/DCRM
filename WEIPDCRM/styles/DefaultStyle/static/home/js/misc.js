var span = $("span.txt"), defTxt = span.text();
span.html('');
$(document).ready(function(){
	run_anim(span, defTxt);
	setInterval(function(){run_anim(span, defTxt)}, 10000);
});
function run_anim(span, defTxt){
	span.fadeOut(500);
	setTimeout(function(){span.html('').fadeIn(0);}, 500);
	setTimeout(function(){typeUrlAnim(span, defTxt);}, 1200);
}
function typeUrlAnim(span, txt){
	var 
	currInx = 0,
	timer = setInterval(function(){
		span.html(txt.slice(7, ++currInx));

		if(currInx >= txt.length){
			clearInterval(timer);
		}
	}, 160);
}