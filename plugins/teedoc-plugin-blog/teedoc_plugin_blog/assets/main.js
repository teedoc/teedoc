
window.onload = function(){
}

$(document).ready(function(){
    var isBlogHome = $("#blog_list").length > 0;
    var isBlog = $("#blog_start").length > 0;
    if(isBlogHome){
        $("#toc").remove();
    }
    function onDownloadOk(data, arg1, arg2){
        var pathname   = window.location.pathname;
        $("#blog_list").append("<ul></ul>");
        for(var url in data["items"]){
            item = data["items"][url];
            var info = '<div class="blog_info"><span class="blog_author">'+ item["author"] + '</span><span class="blog_date">'+ item["date"]+ '</span></div><div class="blog_tags">';
            // list
            // if(isBlogHome){
                var li = '<li><a href="' + url + '" class="blog_title"><h2>'+ item["title"] +'</h2>';
                for(var i in item["tags"]){
                    info += '<span>' + item["tags"][i] + '</span>';    
                }
                info +='</div>' 
                info += '<div class="blog_cover"><img src="' + item["cover"] + '"/></div>';
                li += info + '<div class="blog_brief">'+ item["brief"] +'</div></a></li>';
                $("#blog_list > ul").append(li);
            // }
            // sidebar
            var active = "not_active";
            if(pathname == url){
                active = "active";
            }
            li = '<li class="'+ active +' with_link"><a href="'+ url +'"><span class="label">'+item["title"]+'</span><span class=""></span></a><div class="tip">'+ info +'</div></li>'
            $("#sidebar > ul").append(li);
        }
    }
    function downloadJson(url, callback, arg1=null, arg2=null){
        $.ajax({
            type: "GET",
            url: url,
            contentType: "application/json",
            dataType: "json",
            success: function(data){
                callback(data, arg1, arg2);
            },
            error: function(){
                alert("download index.json fail, please check your internet");
            }
        });
    }
    if(isBlog){
        downloadJson("${site_root_url}static/blog_index/index.json", onDownloadOk);
    }
});

