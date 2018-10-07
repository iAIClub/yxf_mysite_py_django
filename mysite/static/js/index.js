//jquery：在DOM完全就绪时自动执行(这并不意味着这些元素关联的文件都已经下载完毕)
$(document).ready(function(){

	//活动栏目
	$("#navbar a").click(
		function(){
			$(this).addClass("active");
		}
	);

	//切换侧边栏
	$(".navbar-header a").first().click(
		function(){
			$("#left").toggleClass("hidden-xs");
		}
	);

	//回到顶部
	var timer  = null;
	$("#go-top").click(
		function(){
			cancelAnimationFrame(timer);
		    timer = requestAnimationFrame(function fn(){
		        var oTop = document.body.scrollTop || document.documentElement.scrollTop;
		        if(oTop > 0){
		            document.body.scrollTop = document.documentElement.scrollTop = oTop - 60;
		            timer = requestAnimationFrame(fn);
		        }else{
		            cancelAnimationFrame(timer);
		        }
		    });
		}
	);

	//显示二维码
	$("#qr").mouseenter(
		function(){
			var qrstatus = $("#toolbar .qrcode").css("display");
			if(qrstatus == "none"){
				$("#toolbar .qrcode").fadeIn();
				//$("#qrcode").delay(5000).fadeOut();
			}else{
				$("#toolbar .qrcode").fadeOut();
			}
		}
	);

	//
});

//js原生：在所有资源全部加载渲染完成后再执行（完全下载所有的图片、iframe等）
window.onload = function (){
	//func1();
	//func2();
}