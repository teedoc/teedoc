(function(){
    var theme = getTheme();
    setTheme(theme);
}());

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
        $("body").addClass("dark");
        addCss("${site_root_url}static/css/theme_default/dark.css");
    }else{
        obj.removeClass("dark");
        obj.addClass("light");
        $("body").removeClass("dark");
        removejscssfile("${site_root_url}static/css/theme_default/dark.css", "css");
    }
    localStorage.setItem("theme", theme);
}
