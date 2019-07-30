var s="X_ 0123456789abcdef"
for (var i=0;i<16;i++){
  s+="\n"+i.toString(16)+"X ";
  for (var j=0;j<16;j++){
    s+=String.fromCharCode((i<<4)|j);
  }
}