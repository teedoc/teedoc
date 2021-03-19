
jQuery.fn.highlight = function (pat) {
    function innerHighlight(node, pat) {
        var skip = 0;
        if (node.nodeType == 3) {
            var pos = node.data.toUpperCase().indexOf(pat);
            if (pos >= 0) {
                var spannode = document.createElement('span');
                spannode.className = 'highlight';
                var middlebit = node.splitText(pos);
                var endbit = middlebit.splitText(pat.length);
                var middleclone = middlebit.cloneNode(true);
                spannode.appendChild(middleclone);
                middlebit.parentNode.replaceChild(spannode, middlebit);
                skip = 1;
            }
        }
        else if (node.nodeType == 1 && node.childNodes && !/(script|style)/i.test(node.tagName)) {
            for (var i = 0; i < node.childNodes.length; ++i) {
                i += innerHighlight(node.childNodes[i], pat);
            }
        }
        return skip;
    }
    return this.each(function () {
        innerHighlight(this, pat.toUpperCase());
    });
};

window.onload = function(){
}

$(document).ready(function(){
    var waiting_search = false;
    var search_index = null;
    var search_content = {
        "curr": null,
        "others":{}
    }
    function onDownloadOk(data, arg1, arg2){
        search_index = data;
        var pathname   = window.location.pathname;
        var curr_url   = null;
        var others_url = [];
        for(var url in search_index){
            if(pathname.indexOf(url) != -1){
                if(!curr_url){
                    curr_url = url;
                }else{  // already have math item, e.g. `/get_started/zh/install/index.html /get_started/zh`
                        // and now `/get_started/zh/install/index.html /`
                        // choose longger one
                    if(url.length > curr_url.length){
                        others_url.push(curr_url);
                        curr_url = url;
                    }else{
                        others_url.push(url);
                    }
                }
            }else{
                others_url.push(url);
            }
        }
        if(search_index[curr_url]){
            downloadJson(search_index[curr_url], onIndexDownloadOk, curr_url, true);
        }
        for(var i in others_url){
            url = others_url[i];
            downloadJson(search_index[url], onIndexDownloadOk, url, false);
        }
    }
    function onIndexDownloadOk(data, url, is_curr){
        if(is_curr){
            search_content["curr"] = data;
        }else{
            search_content["others"][url] = data;
        }
        if(waiting_search == true){
            waiting_search = false;
            onSearch();
        }
    }
    downloadJson("${site_root_url}static/search_index/index.json", onDownloadOk);
    var input_hint = $("#search_input_hint").html();
    var loading_hint = $("#search_loading_hint").html();
    var download_err_hint = $("#search_download_err_hint").html();
    var other_docs_result_hint = $("#search_other_docs_result_hint").html();
    var curr_doc_result_hint = $("#search_curr_doc_result_hint").html();
    $("body").append('<div id="search_wrapper">\
        <div>\
            <div id="search_content">\
                <div id="search_title">\
                    <div>\
                        <input id="search_input" placeholder="'+ input_hint +'"/>\
                    </div>\
                </div>\
                <div id="search_result">\
                </div>\
            </div>\
        </div><a class="close"></a></div>');
    $("#search").bind("click", function(e){
        $("#search_wrapper").show();
        $("#search_input").focus();
        $("#wrapper").addClass("blur");
        $("#navbar").addClass("blur");
    });
    $("#search_wrapper .close").bind("click", function(e){
        $("#search_wrapper").hide();
        $("#wrapper").removeClass("blur");
        $("#navbar").removeClass("blur");
    });
    $("#search_input").bind("input propertychange", function(){
        setTimeout(() => {
            onSearch();
        }, 1000);
    });
    function onSearch(){
        $("#search_result").empty();
        $("#search_result").append('<ul id="search_curr_result"><div class="hint">'+ curr_doc_result_hint +'</div></ul>');
        $("#search_result").append('<ul id="search_others_result"><div class="hint">'+ other_docs_result_hint +'</div></ul>');
        if(!search_index){
            $("#search_result").append('<div class="search_loading_hint">'+ loading_hint +'</div>');
            waiting_search = true;
            return;
        }
        if(!search_content["curr"] && search_content["others"].length == 0){
            $("#search_result").append('<div class="search_loading_hint">'+ loading_hint +'</div>');
            waiting_search = true;
            return;
        }
        $("#search_curr_result > .hint").addClass("searching");
        var search_keywords = $("#search_input").val();
        search_doc(search_content["curr"], "#search_curr_result");
        for(var url in search_content["others"]){
            search_doc(search_content["others"][url], "#search_others_result");
        }
        function search_doc(data, containerId){
            for(var url in data){
                var content = data[url];
                search_keywords = search_keywords.trim();
                if(search_keywords.length <= 0){
                    return;
                }
                var keywords = search_keywords.split(" ");
                var find = false;
                var find_strs = "";
                for(var i in keywords){
                    var keyword = keywords[i];
                    if(content["title"] && content["title"].indexOf(keyword) >= 0){
                        find = true;
                    }
                }
                if(content["raw"] && content["raw"].length > 0){
                    find_strs = search(keywords, content["raw"]);
                    if(find_strs.length > 0){
                        find = true; 
                    }
                }
                if(find){
                    $(containerId).append('<li><a href="'+ url + '?highlight=' + search_keywords + '"><h1>'+ (data[url]["title"]?data[url]["title"]:url) +
                            '</h1><div>' + find_strs + '</div></a></li>');
                }
            }
        }
        $("#search_curr_result > .hint").removeClass("searching");
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
                $("#search_result").empty();
                $("#search_result").append('<div class="search_download_err_hint">'+ download_err_hint + ': '+ url +'</div>');
            }
        });
    }
    highlightKeywords();
});

function highlightKeywords(){
    var highlight_keywords = getQueryVariable("highlight");
    if(highlight_keywords){
        var highlight_keywords = decodeURI(highlight_keywords);
        highlight_keywords = highlight_keywords.split(" ");
        for(var i=0; i<highlight_keywords.length; ++i){
            console.log(highlight_keywords[i]);
            $('#content_body').highlight(highlight_keywords[i]);
        }
    }
}
function getQueryVariable(variable)
{
       var query = window.location.search.substring(1);
       var vars = query.split("&");
       for (var i=0;i<vars.length;i++) {
               var pair = vars[i].split("=");
               if(pair[0] == variable){return pair[1];}
       }
       return(false);
}
function search(keywords, content, show_length = 15){
    if(keywords.length <= 0){
        return "";
    }
    function _search(keywords, content, idx_rel = 0){
        var idxs = [];
        for(var i in keywords){
            var keyword = keywords[i];
            var idx = content.indexOf(keyword);
            if(idx >= 0){
                idxs.push({
                    "idx": idx + idx_rel,
                    "len": keyword.length
                });
                _idxs = _search([keyword], content.substr(idx + keyword.length), idx_rel + idx + keyword.length);
                idxs = idxs.concat(_idxs);
            }
        }
        return idxs
    }
    var find_strs = "";
    idxs = _search(keywords, content);
    idxs = idxs.sort((a, b)=> a.idx-b.idx);
    var idx_last = -1;
    var len_last = 0;
    for(var i=0; i<idxs.length; ++i){
        var idx = idxs[i]['idx'];
        var len = idxs[i]['len'];

        if(idx_last >= 0 && (idx - idx_last -len_last) < show_length){ // last keyword too close
            find_strs += content.substr(idx_last + len_last, idx - (idx_last + len_last)) + '<code class="highlight">'+ content.substr(idx, len) +'</code>'
        }else{
            var start_idx = (idx - show_length < 0) ? 0 : (idx - show_length);
            find_strs += '...' + content.substr(start_idx,  idx - start_idx) +
                '<code class="highlight">' + content.substr(idx,  len) + 
                '</code>';
        }
        var idx_next = -1;
        if(i < idxs.length -1){
            idx_next = idxs[i + 1]['idx'];
        }
        if(idx_next >= 0 && ((idx_next - idx - len) < show_length) ){ // next keywor too close
        }else{
            find_strs += content.substr(idx + len,  show_length) + '...';
        }
        idx_last = idx;
        len_last = len;
    }
    return find_strs
}

