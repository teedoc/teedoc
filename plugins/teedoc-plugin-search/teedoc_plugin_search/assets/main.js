window.onload = function(){
}

$(document).ready(function(){
    var search_index = null;
    function onDownloadOk(data){
        search_index = data;
    }
    downloadJson("${site_root_url}static/search_index/index.json", onDownloadOk);
    $("body").append('<div id="search_wrapper">\
        <div>\
            <div id="search_content">\
                <div id="search_title">\
                    <div>\
                        <input id="search_input" placeholder="Search"/>\
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
        if(!search_index){
            console.log("search index file not download yet");
            return;
        }
        var search_keywords = $(this).val();
        // console.log(search_index);
        var pathname   = window.location.pathname;
        var curr_url   = null;
        var others_url = [];
        for(var url in search_index){
            if(pathname.indexOf(url) != -1){
                curr_url = url;
            }else{
                others_url.push(url);
            }
        }
        function onCurrDoc(data){
            // console.log(data);
            $("#search_result").empty();
            $("#search_result").append('<ul id="search_curr_result"></ul>');
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
                    if(content["title"].indexOf(keyword) >= 0){
                        find = true;
                    }
                }
                find_strs = search(keywords, content["raw"]);
                if(find_strs.length > 0){
                    find = true; 
                }
                if(find){
                    $("#search_curr_result").append('<li><a href="'+ url + '"><h1>'+ (data[url]["title"]?data[url]["title"]:url) +
                            '</h1><div>' + find_strs + '</div></a></li>');
                }
            }
            // for(var i in others_url){
            //     url = others_url[i]
            //     console.log("other", search_index[url]);
            // }
        }
        // console.log("curr", search_index[curr_url]);
        downloadJson(search_index[curr_url], onCurrDoc)
    });
});


function downloadJson(url, callback){
    $.ajax({
        type: "GET",
        url: url,
        contentType: "application/json",
        dataType: "json",
        success: function(data){
            callback(data);
        },
        error: function(){
            console.log("download index file error, request fail");
        }
    });
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

