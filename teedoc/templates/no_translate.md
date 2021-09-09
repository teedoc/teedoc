---
title: no_translate_title
class: md_page
---


<div id="visit_from"></div>
<div id="no_translate_hint"></div>
<div>
    <span id="visit_hint"></span>
    <a id="translate_src"></a>
</div>

<div>
    <script>
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
        var ref = getQueryVariable("ref");
        var from = getQueryVariable("from");
        var link = document.getElementById("translate_src");
        var fromDis = document.getElementById("visit_from");
        link.href = ref;
        link.text = ref;
        fromDis.innerHTML = from;
    </script>
</div>

