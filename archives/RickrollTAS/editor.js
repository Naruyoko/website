function dg(s){
  return document.getElementById(s);
}

window.onload=function (){
  initializeAudio();
  initializeTable();
  setInterval(playerLoop);
}

var SOUNDS=["snareLA", "snareC", "snareF", "snareF#", "basedrum", "snare", "plingLG#", "plingC#", "plingD#", "plingF", "plingF#", "plingG#", "plingHC#", "xyloLG#", "xyloLA#", "xyloC", "xyloC#", "xyloD#", "xyloF", "xyloG#", "bassLF#", "bassLG#", "bassLA#", "bassC", "bassD#", "bassF", "bassF#", "bassG#", "bassA#", "bassHC", "bassHC#", "bassHD#", "bassHF", "C#6chord", "Fm7chord", "G#chord", "F#M7chord"];
var AUDIOS={};
var tape=[];
var tapelen=0;
var TABLEWIDTH=50;
var scrollpos=0;
var mouseoverpos=[-1,-1];
var TICKRATE=20;
var playing=false;
var playstartpos=0;
var playpos=0;
var startTime;
var table;
var PLAYMAXRELPOS=20;
var TICKS_PER_BEAT=10;
var BEATS_PER_MEASURE=4;

function initializeAudio(){
  for (var i=0;i<SOUNDS.length;i++){
    AUDIOS[SOUNDS[i]]=new Howl({src:["./sounds/"+encodeURIComponent(SOUNDS[i])+".wav"]});
  }
}
function playSound(name){
  if (AUDIOS[name]) AUDIOS[name].play();
}
function setAction(tick,value){
  if (tape[tick]) tape[tick].action=value;
  else tape[tick]={action:value,hasdummy:false};
}
function getAction(tick){
  if (tape[tick]) return tape[tick].action;
  else return "";
}
function setHasdummy(tick,value){
  if (tape[tick]) tape[tick].hasdummy=value;
  else tape[tick]={action:"",hasdummy:value};
}
function getHasdummy(tick){
  if (tape[tick]) return tape[tick].hasdummy;
  else return false;
}
function initializeTable(){
  table=dg("tableio");
  for (var i=0;i<=SOUNDS.length+2;i++){
    var row=table.insertRow(-1);
    for (var j=0;j<TABLEWIDTH+1;j++){
      var cell=row.insertCell(-1);
      if (i>0&&j===0){
        if (i==SOUNDS.length+1){
          cell.textContent="hasdummy";
        }else if (i==SOUNDS.length+2){
          cell.textContent="action";
        }else{
          cell.textContent=SOUNDS[i-1];
        }
      }
      if (j>0) cell.style.textAlign="center";
      if (j>0&&i==SOUNDS.length+2) cell.classList.add("rotated");
      cell.onclick=function (i,j){return function (e){onCellClick(e,i,j)};}(i,j);
      cell.onmouseover=function (i,j){return function (e){onCellMouseover(e,i,j)};}(i,j);
      cell.onmouseout=function (i,j){return function (e){onCellMouseout(e,i,j)};}(i,j);
    }
  }
  requestUpdate();
}
function updateTable(){
  scrollpos=+dg("tablescroll").value;
  for (var i=0;i<=SOUNDS.length+2;i++){
    for (var j=0;j<TABLEWIDTH+1;j++){
      var cell=table.rows[i].cells[j];
      var content,bgcolor;
      var tickpos=scrollpos+j-1;
      if (j===0){
        content=cell.textContent;
      }else if (i===0){
        content=tickpos;
      }else if (i===SOUNDS.length+1){
        content=getHasdummy(tickpos)?"\u2b24":"";
      }else if (i===SOUNDS.length+2){
        content=getAction(tickpos)||"";
      }else{
        content=getAction(tickpos)==SOUNDS[i-1]?"\u2b24":"";
      }
      bgcolor="";
      if (tickpos%TICKS_PER_BEAT===0){
        bgcolor="#ddd";
      }
      if (tickpos%(TICKS_PER_BEAT*BEATS_PER_MEASURE)===0){
        bgcolor="#aaa";
      }
      if (i==mouseoverpos[1]||j==mouseoverpos[0]){
        bgcolor="#faa";
      }
      if (scrollpos+j-1==playpos){
        bgcolor="#afa";
      }
      cell.textContent=content;
      cell.style.backgroundColor=bgcolor;
    }
  }
}
var isRequested=false;
function requestUpdate(){
  if (!isRequested) requestAnimationFrame(function(){
    isRequested=false;
    updateTable();
  });
}
function updateTapelen(){
  tapelen=Math.max(tape.length,playpos);
}
function onCellClick(e,y,x){
  //console.log([x,y]);
  e.preventDefault();
  var tickpos=scrollpos+x-1;
  if (x===0){
  }else if (y===0){
    playstartpos=playpos=scrollpos+x-1;
    startTime=Date.now();
  }else if (y==SOUNDS.length+1){
    setHasdummy(tickpos,!getHasdummy(tickpos));
  }else if (y==SOUNDS.length+2){
    var newraw=prompt("Enter raw",getAction(tickpos)||"");
    if (newraw!==null) setAction(tickpos,newraw);
  }else{
    if (getAction(tickpos)==SOUNDS[y-1]){
      setAction(tickpos,"");
    }else{
      setAction(tickpos,SOUNDS[y-1]);
    }
  }
  if (y>0&&y<=SOUNDS.length) playSound(SOUNDS[y-1]);
  while (tape.length&&!getAction(tape.length-1)&&!getHasdummy(tape.length-1)) tape.pop();
  updateTapelen();
  updateScrollPos();
  requestUpdate();
}
function onCellMouseover(e,y,x){
  //console.log([x,y]);
  mouseoverpos=[x,y];
  requestUpdate();
}
function onCellMouseout(e,y,x){
  //console.log([x,y]);
  mouseoverpos=[-1,-1];
  requestUpdate();
}
function play(){
  playpos=playstartpos-1;
  startTime=Date.now();
  playing=true;
  scrollToPlaypos();
}
function pause(){
  playpos=playstartpos;
  playing=false;
  requestUpdate();
}
function toggleplay(){
  if (playing) pause();
  else play();
}
function scrollToPlaypos(){
  if (scrollpos>playpos){
    setScrollPos(playpos);
  }
  if (playpos>tapelen){
    pause();
  }
}
function playerLoop(){
  if (!playing) return;
  var time=Date.now();
  var tick=Math.floor((time-startTime)/1000*TICKRATE)+playstartpos;
  while (playpos<tick){
    playpos++;
    if (getAction(playpos)) playSound(getAction(playpos));
  }
  scrollToPlaypos();
  if (PLAYMAXRELPOS<playpos-scrollpos){
    setScrollPos(playpos-PLAYMAXRELPOS);
  }
  requestUpdate();
}
function updateScrollPos(){
  dg("tablescroll").max=tapelen;
  scrollpos=+dg("tablescroll").value;
  requestUpdate();
}
function setScrollPos(value){
  dg("tablescroll").value=scrollpos=value;
  updateScrollPos();
}
function exporttext(){
  if (!confirm("Do you wish to EXPORT?")) return;
  var lines=[];
  for (var i=0;i<tape.length;i++){
    if (getAction(i)) lines.push(i+(tape[i].hasdummy?"*":"")+";"+tape[i].action);
  }
  dg("textio").value=lines.join("\n");
}
function importtext(){
  if (!confirm("Do you wish to IMPORT?")) return;
  var lines=dg("textio").value.split("\n");
  tape=[];
  for (var i=0;i<lines.length;i++){
    if (lines[i]){
      var semicolonpos=lines[i].indexOf(";");
      var hasdummy=lines[i][semicolonpos-1]=="*";
      var tick=+lines[i].slice(0,hasdummy?semicolonpos-1:semicolonpos);
      if (isFinite(tick)) tape[tick]={action:lines[i].slice(semicolonpos+1),hasdummy:hasdummy};
    }
  }
  updateTapelen();
  updateScrollPos();
  requestUpdate();
}
function handlekeybinds(e){
  if (document.activeElement&&(document.activeElement.nodeName.toLowerCase()=="input"||document.activeElement.nodeName.toLowerCase()=="textarea")) return;
  var key=e.code;
  var wasCaught=true;
  if (key=="Space"){
    toggleplay();
  }else if (e.shiftKey&&key=="ArrowLeft"){
    if (playing){
      playpos-=TICKRATE;
      startTime=Date.now()-(playpos-playstartpos)/TICKRATE*1000;
      scrollToPlaypos();
    }else{
      playpos=playstartpos=Math.max(playstartpos-1,0);
    }
    requestUpdate();
  }else if (e.shiftKey&&key=="ArrowRight"){
    if (playing){
      playpos+=TICKRATE;
      startTime=Date.now()-(playpos-playstartpos)/TICKRATE*1000;
      scrollToPlaypos();
    }else{
      playpos=playstartpos=Math.min(playstartpos+1,tapelen);
    }
    requestUpdate();
  }else if (!e.shiftKey&&key=="ArrowLeft"){
    setScrollPos(scrollpos-1);
  }else if (!e.shiftKey&&key=="ArrowRight"){
    setScrollPos(scrollpos+1);
  }else{
    wasCaught=false;
  }
  if (wasCaught) e.preventDefault();
} 
window.addEventListener("keydown",handlekeybinds);