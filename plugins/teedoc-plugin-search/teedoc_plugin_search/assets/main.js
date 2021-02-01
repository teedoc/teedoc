window.onload = function(){
}

$(document).ready(function(){
    $("body").append('<div id="search_wrapper"><div id="search_content">\
        <div id="search_title">\
            <div>\
                <input placeholder="Search"/>\
            </div>\
        </div>\
        <div id="search_result">\
        </div>\
        </div><a class="close"></a></div>');
    $("#search").bind("click", function(e){
        $("#search_wrapper").show();
    });
    $("#search_wrapper .close").bind("click", function(e){
        $("#search_wrapper").hide();
    });
});
