/*
次のJavaScript(ES6) のプログラムで、consoleに出力される数を「スパゲテイ数」とする。
ただし、Numberは無限の精度と最大値(理論上の値を計算する)を持ち、また全ての型について、メモリは無限大にあるとする。
また、スタックは無限の大きさを持つとする。
また、おかしな部分があったとしても、そのままプログラムを取るとする。
スコープがおかしなことになっていてもそれは仕様。
停止性? そんなものは知らん。おそらく止まると思うが。
*/

var r=100;
var f=x=>x**x;r++;
var g=""+
"    Spagetii     \n"+
"                 \n"+
"                 \n"+
"       _--_-_    \n"+
"    __- / \\/\\    \n"+
"   /_-- /-/  \\_  \n"+
"   =__-//\\__--_  \n"+
"  \\___________/  \n"+
"   \\___=-=___/   \n"+
"    ---------    \n";
var q=function (a){
  if (!a) return r;
  var c=a[0];
  var d=a.substring(1);
  if (c==" "){
    for (var i=r;i;i--){
      r=f(q(d));
    }
    return r;
  }
  else if (c=="\n"){
    for (var i=r;i;i--){
      r=f(q(d.split("\n").map(e=>e.repeat(r)).join("\n")));
    }
    return r;
  }
  else if (c=="_"){
    f=new Function("for(var i=x;i;i--)x=("+f+")(x);return x");
    return q(d);
  }
  else if (c=="="){
    if (c%10)
      if (c%3) return r=q(d[0].repeat(r)+d.substring(1));
    else return r=q(d.split("\n").map(e=>e.includes("=")?e:e.repeat(r)).join("\n"));
    return q(d); //this shouldn't be reached
  }
  else if (c=="-"){
    return r=f(q(d));
  }
  else if (c=="/"){
    var t="";
    for (i in d) t+=d[i].repeat(d[i].charCodeAt());
    return r=q(t);
  }
  else if (c=="\\"){
    var t="";
    for (i in d) t+=d[i]+d.charCodeAt(i);
    return r=q(t);
  }
  else{
    return r=f(q(String.fromCharCode(c.charCodeAt()-1)+d));
  }
}
      
console.log(q(g));