

var conf=js_vars["teedoc-plugin-ad-hint"];
(function(){
    if(!conf.type || conf.type == "null" || conf.type == ""){
        return;
    }
    if(conf.type == "new" || conf.type == "hint"){
        $("#nav_left").append('<li id="new_feature_btn" class="sub_items"><a>'+conf.label+'</a></li>');
        $("#navbar").before('<div id="new_feature_content"><div><span class="content">'+conf.content+'</span><span class="close">x</span><div></div>')
        $("#new_feature_btn").bind("click", function(){
            $("#new_feature_content").slideToggle();
        });
        $("#new_feature_content .close").bind("click", function(){
            $("#new_feature_content").slideUp();
        });
        if(conf.show_times > 0){ // only show some times and disapear
            var date = null;
            if(conf.date){
                date = new Date(conf.date).getTime()/1000;
            }
            var times = show_time(-1, date);
            if(date && (new Date().getTime()/1000 < date)){ // always show if not reach date
                times = -1;
            }
            if(times == 0){
                return;
            }
            if(times < 0){
                times = conf.show_times;
            }
            show_time(times - 1, date);
        }
        $("#new_feature_content").slideDown();
    }
})();

function show_time(times = -1, date_ts=null){
    if(times < 0){
        var s = localStorage.getItem("hint_show_times");
        if(!s){
            times = -1;
        }else{
            var o = JSON.parse(s);
            var now = new Date().getTime()/1000;
            if((now - o.ts > conf.show_after_s) || !("update" in o) || (date_ts && o.update && (o.update < date_ts)) || (date_ts && !o.update) ){ // timeout or have new info
                times = -1;
            }else{
                times = o.times;
            }
        }
        return times;
    }else{
        localStorage.setItem("hint_show_times", JSON.stringify({
            "times": times,
            "ts": new Date().getTime()/1000,
            "update": date_ts
        }));
    }
}

