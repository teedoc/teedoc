
window.onload = function(){
}

$(document).ready(function(){
    $("#sidebar ul > li ul ").addClass("collapsed");
    $("#sidebar .sub_indicator").addClass("sub_indicator_collapsed")
    registerSidebarClick();
});

function registerSidebarClick(){
    $("#sidebar ul li > a").bind("click", function(e){
        var o_dirs = $(this).next();
        var collapsed = o_dirs.hasClass("collapsed");
        if(collapsed){
            o_dirs.removeClass("collapsed");
            $(this).children(".sub_indicator").removeClass("sub_indicator_collapsed");
        }else {
            o_dirs.addClass("collapsed");
            $(this).children(".sub_indicator").addClass("sub_indicator_collapsed");
        }
    });
}

