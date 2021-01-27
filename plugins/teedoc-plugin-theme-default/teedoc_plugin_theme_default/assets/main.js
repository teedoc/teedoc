
(function () {
    var elements = document.getElementsByTagName("pre");
    for(var i=0; i<elements.length; ++i){
        elements[i].classList.add("language-none");
        elements[i].classList.add("line-numbers");
    }
    // $('pre').addClass("language-none");
    // $('pre').addClass("line-numbers").css("white-space", "pre-wrap");
}());

window.onload = function(){
}

$(document).ready(function(){
    $("#sidebar ul .show").slideDown(200);
    registerSidebarClick();
});

function registerSidebarClick(){
    function show_collapse_item(a_obj){
        var o_ul = a_obj.next();
        var collapsed = !o_ul.hasClass("show");
        if(collapsed){
            o_ul.slideDown(200);
            o_ul.removeClass("collapsed");
            o_ul.addClass("show");
            a_obj.children(".sub_indicator").removeClass("sub_indicator_collapsed");
        }else {
            o_ul.slideUp(200);
            o_ul.removeClass("show");
            o_ul.addClass("collapsed");
            a_obj.children(".sub_indicator").addClass("sub_indicator_collapsed");
        }
    }
    $("#sidebar ul li > a").bind("click", function(e){
        var is_click_indicator = $(e.target).hasClass("sub_indicator");
        var a_obj = $(this);
        if(a_obj.attr("href") == window.location.pathname){
            show_collapse_item(a_obj);
            return false;
        }
        show_collapse_item(a_obj);
        if(is_click_indicator){ // click indicator, only collapse, not jump to link
            return false;
        }
    });
    $("#menu").bind("click", function(e){
        $("#sidebar_wrapper").toggle();
        $("#to_top").toggle();
        if($("#menu").hasClass("menu_fixed")){
            $("#menu").removeClass("menu_fixed");
            $("#menu").removeClass("close");
        }else{
            $("#menu").addClass("menu_fixed");
            $("#menu").addClass("close");
        }
    });
    $("#navbar_menu_btn").bind("click", function(e){
        $("#navbar_items").toggle();
    });
    var theme = getTheme();
    setTheme(theme);
    $("#themes").bind("click", function(e){
        var obj = $("#themes");
        if(obj.hasClass("light")){
            setTheme("dark");
        }else {
            setTheme("light");
        }
    });
}


function addCss(filename) {
    var creatHead = $('head');
    creatHead.append('<link rel="stylesheet" href="' + filename + '" type="text/css">')
}
function removejscssfile(filename, filetype) {
    var targetelement = (filetype == "js") ? "script" : (filetype == "css") ? "link" : "none"
    var targetattr = (filetype == "js") ? "src" : (filetype == "css") ? "href" : "none"
    var allsuspects = document.getElementsByTagName(targetelement)
    for (var i = allsuspects.length; i >= 0; i--) {
        if (allsuspects[i] && allsuspects[i].getAttribute(targetattr) != null && allsuspects[i].getAttribute(targetattr).indexOf(filename) != -1)
            allsuspects[i].parentNode.removeChild(allsuspects[i])
    }
}


function getTheme(){
    var t = localStorage.getItem("theme");
    if(!t){
        t = "light";
        setTheme(t);
    }
    return t;
}
function setTheme(theme){
    var obj = $("#themes");
    if(theme=="dark"){
        obj.removeClass("light");
        obj.addClass("dark");
        addCss("/static/css/theme_default/dark.css");
        // removejscssfile("/static/css/theme_default/light.css", "css");
    }else{
        obj.removeClass("dark");
        obj.addClass("light");
        // addCss("/static/css/theme_default/light.css");
        removejscssfile("/static/css/theme_default/dark.css", "css");
    }
    localStorage.setItem("theme", theme);
}
