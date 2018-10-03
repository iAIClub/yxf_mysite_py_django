$(document).ready(
	function(){
		$(".navbar-header a").first().click(
			function(){
				$(".sidebar").toggle();
			}
		);
	}
);
$(document).ready(
	function(){
		$("#navbar a").click(
			function(){
				$(this).addClass("active");
			}
		);
	}
);