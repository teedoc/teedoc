
window.onload = function(){
}

jQuery.fn.onPositionChanged = function (trigger, millis) {
    if (millis == null) millis = 100;
    var o = $(this[0]); // our jquery object
    if (o.length < 1) return o;

    var lastPos = null;
    var lastOff = null;
    setInterval(function () {
        if (o == null || o.length < 1) return o; // abort if element is non existend eny more
        if (lastPos == null) lastPos = o.position();
        if (lastOff == null) lastOff = o.offset();
        var newPos = o.position();
        var newOff = o.offset();
        if (/*lastPos.top != newPos.top ||*/ lastPos.left != newPos.left) {
            $(this).trigger('onPositionChanged', { lastPos: lastPos, newPos: newPos });
            if (typeof (trigger) == "function") trigger(lastPos, newPos);
            lastPos = o.position();
        }
        if (/*lastOff.top != newOff.top ||*/ lastOff.left != newOff.left) {
            $(this).trigger('onOffsetChanged', { lastOff: lastOff, newOff: newOff});
            if (typeof (trigger) == "function") trigger(lastOff, newOff);
            lastOff= o.offset();
        }
    }, millis);

    return o;
};

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
        function adjustTipPos(){
            let menu = $("#menu");
            let pos = menu.position();
            let tip = $("#sidebar .tip");
            console.log(pos, tip);
            tip.css("top", pos.top - document.documentElement.scrollTop + menu.height() + "px");
            tip.css("left", pos.left + "px");
        }
        adjustTipPos();
        $("#menu").onPositionChanged(adjustTipPos);        // horizontal
        document.addEventListener("scroll", adjustTipPos); // vertical
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

