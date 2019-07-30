var s="X_ 0123456789abcdef"
for (var i=0;i<8;i++){
  s+="\n"+i+"X ";
  for (var j=0;j<16;j++){
    s+=String.fromCharCode((i<<4)|j);
  }
}