

$(document).ready(function(){
    if("${type}" == "null" || "${type}" == ""){
        return;
    }
    if("${type}" == "new"){
        $("#nav_left").append('<li id="new_feature_btn" class="sub_items"><a>New</a></li>');
        $("#navbar").before('<div id="new_feature_content"><div><span class="content">${content}</span><span class="close">x</span><div></div>')
        $("#new_feature_btn").bind("click", function(){
            $("#new_feature_content").slideDown();
        });
        $("#new_feature_content .close").bind("click", function(){
            $("#new_feature_content").slideUp();
        });
        // var url = "";
        // if("${url}" != "null"){
        //     url = "${url}";
        // }
        // $("#new_feature_btn").append('<ul><li class=""><a href="' + url +'" target="${target}">${brief}</a></li></ul>')
        if(${show_times} > 0){ // only show some times and disapear
            var times = show_time();
            if(times == 0){
                return;
            }
            if(times < 0){
                times = ${show_times};
            }
            show_time(times - 1, ${show_times});
        }
        $("#new_feature_content").slideDown();
        // $("#navbar #new_feature_btn > ul").addClass("visible_top");
        // setTimeout(function(){
        //     $("#navbar #new_feature_btn > ul").removeClass("visible_top");
        // }, 3000);
        
    }
    // $("body").append('<div id="hint_container"><div class="close">X</div><div id="hint_content">${content}</div></div>');
});

function show_time(times = -1){
    if(times < 0){
        var s = localStorage.getItem("hint_show_times");
        if(!s){
            times = -1;
        }else{
            var o = JSON.parse(s);
            if(new Date().getTime()/1000 - o.ts > ${show_after_s}){
                times = -1;
            }else{
                times = o.times;
            }
        }
        return times;
    }else{
        localStorage.setItem("hint_show_times", JSON.stringify({
            "times": times,
            "ts": new Date().getTime()/1000}));
    }
}

