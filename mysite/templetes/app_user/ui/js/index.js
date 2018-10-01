/**/


$(document).ready(function(){
	$("#nav-sidebar-item1>li:nth-child(1)>a").click(function(){
		$("main #main-overview").show();
		$("main #main-analyze").hide();
		$("main #main-export").hide();
	});
	$("#nav-sidebar-item1>li:nth-child(2)>a").click(function(){
		$("main #main-overview").hide();
		$("main #main-analyze").show();
		$("main #main-export").hide();
	});
	$("#nav-sidebar-item1>li:nth-child(3)>a").click(function(){
		$("main #main-overview").hide();
		$("main #main-analyze").hide();
		$("main #main-export").show();
	});
});