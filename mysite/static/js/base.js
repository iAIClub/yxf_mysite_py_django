//jquery：在DOM完全就绪时自动执行(这并不意味着这些元素关联的文件都已经下载完毕)
$(document).ready(function(){
    //layui
    layui.use(['element','form'], function(){
        var element = layui.element;
        var form = layui.form;
    });

	//导航栏活动项目
	$("#navbar .layui-main").find("a").each(
		function(){
            if (this.href == document.location.href){
                $(this).parent().addClass('layui-this');
            }else if(document.location.href.search(this.href) >= 0){
            	$(this).parent().addClass('layui-this');
            }
		}
	);

	//侧边栏活动项目
	$("#left").find("a").each(
		function(){
            if (this.href == document.location.href){
                $(this).addClass('layui-this');
            }else if(document.location.href.search(this.href) >= 0){
            	if($("#left .layui-this").length>0){}else{$(this).addClass('layui-this');}
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
	$("#page").scroll(function(){
        //当window的scrolltop距离大于1时，go to
        if($(this).scrollTop() > 100){
            $('#go-top').fadeIn();
        }else{
            $('#go-top').fadeOut();
        }
    });
    $("#go-top").click(function(){
        $("#page").animate({scrollTop: 0}, 1000);
    });

	//显示二维码
	$("#qr").mouseenter(
		function(){
			var qrstatus = $("#toolbar .qrcode").css("display");
			if(qrstatus == "none"){
				$("#toolbar .qrcode").fadeIn();
			}else{
				$("#toolbar .qrcode").fadeOut();
			}
		}
	);
});
