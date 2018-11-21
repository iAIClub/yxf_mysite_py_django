//jquery：在DOM完全就绪时自动执行(这并不意味着这些元素关联的文件都已经下载完毕)
$(document).ready(function(){

	//导航栏活动项目
	$("#navbar-collapse:first").find("a").each(
		function(){
            if (this.href == document.location.href){
                $(this).parent().addClass('active');
            }else if(document.location.href.search(this.href) >= 0){
            	$(this).parent().addClass('active');
            }
		}
	);

	//侧边栏活动项目
	$("#left").find("a").each(
		function(){
            if (this.href == document.location.href){
                $(this).addClass('active');
            }else if(document.location.href.search(this.href) >= 0){
            	if($("#left .active").length>0){}else{$(this).addClass('active');}
            }
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
});
