var s="XXX_ 0123456789abcdef"
for (var i=0;i<4096;i++){
  s+="\n";
  if (i>>8){
    s+=i.toString(16);
  }else if (i>>4){
    s+="0"+i.toString(16);
  }else{
    s+="00"+i.toString(16);
  }
  s+="X ";
  for (var j=0;j<16;j++){
    s+=String.fromCharCode((i<<4)|j);
  }
}