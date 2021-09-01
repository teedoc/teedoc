


(function() {{
  var supportedClass=[${supported_classes}]
  var needGitalk = false;
  supportedClass.forEach(function(v, i){
    if(document.getElementsByClassName(v).length > 0){
      needGitalk = true;
    }
  });
  if(!needGitalk){
    return;
  }
  var wrapper = document.getElementById("content_wrapper");
  var node=document.createElement("div");
  node.id = "gitalk-container";
  wrapper.appendChild(node);
  // render
  var config = ${config};
  var html = document.getElementsByTagName("html")[0];
  var id = html.id;
  if(id){
    config["id"] = id;
  }else{
    config["id"] = location.pathname;
  }
  // get attr from html attr set in md metadata
  for (var i=0;i<html.attributes.length;i++){
    var v = html.attributes[i];
    if(v.name.startsWith("gitalk-")){
      var configName = v.name.substr(7)
      if(configName in ["number", "perPage"]){
        config[configName] = parseInt(v.value);
      }else{
        config[configName] = v.value;
      }
    }
  }
  console.log(config);
  var gitalk = new Gitalk(config);
  gitalk.render('gitalk-container');
  
}})();

