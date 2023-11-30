import win32gui
import win32con
import pyautogui
import pydirectinput
import keyboard
import time
import sys
import texttable
import re
import colorama

colorama.init()

# Make command line show up on top
hwnd = win32gui.GetForegroundWindow()
window_name=win32gui.GetWindowText(hwnd)
if window_name.find("cmd.exe")!=-1 and window_name.find("python")!=-1:
  win32gui.SetWindowPos(hwnd,win32con.HWND_TOPMOST,0,0,800,400,0)

adjustpos_file=open(sys.path[0]+"/adjustpos.txt","r")
pianoroll_file=open(sys.path[0]+"/pianoroll.txt","r")

TICKRATE=1
FRAMERATE=30
TRAVELFRAMES=10
SEE_BEFORE=5
SEE_AFTER=10
pyautogui.PAUSE=0
pydirectinput.PAUSE=0

def processInputFile(lines):
  def setAlias(name,args):
    alias={
      "name":name,
      "pitchF":float(args[0]),
      "yawF":float(args[1]),
      "buttons":";".join(args[2:])
    }
    r["aliases"][name]=alias
    return alias
  r={
    "aliases":{},
    "ticks":[],
    "length":0
  }
  for line in lines:
    if line=="":
      continue
    args=line.split(";")
    if args[0]=="set":
      setAlias(args[1],args[2:])
    else:
      hasdummy=args[0][-1]=="*"
      tickstr=args[0][:-1] if hasdummy else args[0]
      if not(tickstr.isnumeric() and int(tickstr)>=0):
        continue
      tick=int(tickstr)
      while len(r["ticks"])<=tick:
        r["ticks"].append({"alias":"default","hasdummy":False})
      if len(args)==2:
        r["ticks"][tick]={"alias":args[1],"hasdummy":hasdummy}
        if args[1] not in r["aliases"]:
          print("\033[93mUnknown alias "+args[1]+" at "+tickstr+"\033[0m")
      else:
        setAlias(tickstr+";",args[1:])
        r["ticks"][tick]={"alias":tickstr+";","hasdummy":hasdummy}
      r["length"]=len(r["ticks"])
  return r

ADJLINES=adjustpos_file.read().splitlines()
ADJARGS=processInputFile(ADJLINES)
ADJTICKLEN=ADJARGS["length"]
PIANOLINES=pianoroll_file.read().splitlines()
PIANOARGS=processInputFile(PIANOLINES)
PIANOTICKLEN=PIANOARGS["length"]
TICKS_BETWEEN=20
TICKS_OFFSET=0

adjustpos_file.close()
pianoroll_file.close()

def tickInRange(list,tick):
  return tick>=0 and tick<list["length"]

def getLineAlias(list,tick):
  if tick<0:
    return "start"
  elif tick>=list["length"] or list["ticks"][tick]["alias"] not in list["aliases"]:
    return "default"
  elif tickInRange(list,tick):
    return list["ticks"][tick]["alias"]

PIXELS_PER_ROTATION=2400
DEGREES_PER_ROTATION=360
def angleFtoP(pitchF,yawF):
  return round(pitchF*PIXELS_PER_ROTATION/DEGREES_PER_ROTATION,0),round(yawF*PIXELS_PER_ROTATION/DEGREES_PER_ROTATION,0)

def splitMouseMovement(args,segn):
  r=[]
  for seg in range(segn):
    lastangle={
      "deltaX":round(args["deltaX"]*seg//segn),
      "deltaY":round(args["deltaY"]*seg//segn)
    }
    thisangle={
      "deltaX":round(args["deltaX"]*(seg+1)//segn),
      "deltaY":round(args["deltaY"]*(seg+1)//segn)
    }
    r.append({
      "deltaX":int(thisangle["deltaX"]-lastangle["deltaX"]),
      "deltaY":int(thisangle["deltaY"]-lastangle["deltaY"])
      })
  return r

def computeLineInfo(list,tick):
  r={}
  lastargs=list["aliases"][getLineAlias(list,tick-1)]
  alias=getLineAlias(list,tick)
  thisargs=list["aliases"][alias]
  r["tick"]=tick
  r["alias"]=alias
  r["hasdummy"]=tickInRange(list,tick) and list["ticks"][tick]["hasdummy"]
  r["pitchF"]=thisargs["pitchF"]
  r["yawF"]=thisargs["yawF"]
  r["pitchP"],r["yawP"]=angleFtoP(r["pitchF"],r["yawF"])
  lastPitchP,lastYawP=angleFtoP(lastargs["pitchF"],lastargs["yawF"])
  leftDistance=(lastPitchP-r["pitchP"]+PIXELS_PER_ROTATION)%PIXELS_PER_ROTATION
  rightDistance=(r["pitchP"]-lastPitchP+PIXELS_PER_ROTATION)%PIXELS_PER_ROTATION
  r["deltaX"]=-leftDistance if leftDistance<rightDistance else rightDistance
  r["deltaY"]=r["yawP"]-lastYawP
  r["buttonsstr"]=thisargs["buttons"]
  r["buttons"]=re.split("(?<!,),(?!,)",r["buttonsstr"])
  for i in range(len(r["buttons"])):
    r["buttons"][i]=re.sub(",(?!,)","",r["buttons"][i])
  return r

table=texttable.Texttable()
table.set_deco(texttable.Texttable.HEADER)
table.set_cols_dtype(["t","i","t","f","f","i","i","i","i","t"])
table.set_cols_align(["l","r","l","r","r","r","r","r","r","l"])
table.set_cols_width([5,4,12,6,6,6,4,6,4,14])
table.set_precision(1)
def drawTable(table,list,now):
  table.reset()
  table.add_row(["","Tick","Alias","PitchF","YawF","PitchP","YawP","DelX","DelY","Buttons"]) #Header
  for tick in range(now-SEE_BEFORE,now+SEE_AFTER):
    args=computeLineInfo(list,tick)
    table.add_row([
      "Play>" if tick==now else "Next>" if tick==now+1 else ":",
      args["tick"],
      args["alias"],
      args["pitchF"],
      args["yawF"],
      args["pitchP"],
      args["yawP"],
      args["deltaX"],
      args["deltaY"],
      args["buttonsstr"]])
  print(table.draw()
    .replace("Play>","\033[42mPlay>",1)
    .replace("Next>","\033[43mNext>",1)
    .replace(":","\033[0m ")
    +"\033[0m")
  return

def doTick(list,now):
  args=computeLineInfo(list,now)
  tick_start_time=time.time()
  mouseMovements=splitMouseMovement(args,TRAVELFRAMES)
  #Move mouse
  if args["hasdummy"]:
    pydirectinput.move(10,10) #Dummy input
  for i in range(TRAVELFRAMES):
    while time.time()-tick_start_time<(i+1)/FRAMERATE:
      continue
    #print([i,mouseMovements[i]["deltaX"],mouseMovements[i]["deltaY"]])
    pydirectinput.move(mouseMovements[i]["deltaX"],mouseMovements[i]["deltaY"])
  #Keys
  for keystr in args["buttons"]:
    if keystr=="":
      continue
    if keystr[0]=="D":
      key=keystr[1:]
      mode="down"
    elif keystr[0]=="U":
      key=keystr[1:]
      mode="up"
    elif keystr[0]=="T":
      key=keystr[1:]
      mode="text"
    else:
      key=keystr
      mode="press"
    #print(keystr,key,mode)
    if mode=="text":
      keyboard.write(key)
      continue
    if key=="click" or key=="lbutton" or key=="lb":
      if mode=="press":
        pydirectinput.click()
      elif mode=="down":
        pydirectinput.mouseDown()
      elif mode=="up":
        pydirectinput.mouseUp()
    elif key=="rbutton" or key=="rb":
      if mode=="press":
        pydirectinput.click(button="right")
      elif mode=="down":
        pydirectinput.mouseDown(button="right")
      elif mode=="up":
        pydirectinput.mouseUp(button="right")
    else:
      if mode=="press":
        keyboard.send(key)
      elif mode=="down":
        keyboard.press(key)
      elif mode=="up":
        keyboard.release(key)

def doTickAndDraw(table,list,now):
  drawTable(table,list,now)
  doTick(list,now)

drawTable(table,ADJARGS,0)
print("Press enter to start")
input()
for i in range(5,0,-1):
  print(i)
  time.sleep(1)

start_time=time.time()
print(start_time)

print("Adjusting player's position")
for tick in range(ADJTICKLEN):
  abstick=tick
  while time.time()-start_time<abstick/TICKRATE:
    continue
  doTickAndDraw(table,ADJARGS,tick)

print("Playing")
for tick in range(TICKS_OFFSET,PIANOTICKLEN):
  abstick=tick+(ADJTICKLEN+TICKS_BETWEEN)-TICKS_OFFSET
  while time.time()-start_time<abstick/TICKRATE:
    continue
  doTickAndDraw(table,PIANOARGS,tick)

exit()