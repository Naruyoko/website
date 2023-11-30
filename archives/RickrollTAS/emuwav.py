import win32gui
import win32con
import wave
import pyautogui
import time
import sys

def exitClean():
  wavefile.close()
  exit()

# Make command line show up on top
hwnd = win32gui.GetForegroundWindow()
window_name=win32gui.GetWindowText(hwnd)
if window_name.find("cmd.exe")!=-1 and window_name.find("python")!=-1:
  win32gui.SetWindowPos(hwnd,win32con.HWND_TOPMOST,100,100,800,600,0)

mode_list=["testload","dumpraw","dumpdc","dumpclicks","run","rundebug"]
mode_list_str="/".join(mode_list)
mode=""
while mode not in mode_list:
  print("Choose from modes: "+mode_list_str+" ?")
  mode=input()
moden=mode_list.index(mode)
# testload
print("Loading file")
file_name=sys.path[0]+"/closingttsreduced.wav"
wavefile=wave.open(file_name,"rb")
FRAMELEN=wavefile.getnframes()
if moden==0:
  print("Channels: "+str(wavefile.getnchannels()))
  print("Sample width: "+str(wavefile.getsampwidth()))
  print("Sampling frequency: "+str(wavefile.getframerate()))
  print("Frames: "+str(FRAMELEN))
  print("Compression type: "+str(wavefile.getcomptype()))
  exitClean()
# dumpraw
print("Reading file")
frames=[]
FRANGE=range(FRAMELEN)
for i in FRANGE:
  frames.append(wavefile.readframes(1))
if moden==1:
  for i in FRANGE:
    print(str(i)+" "+frames[i].hex())
  exitClean()
# dumpdc
print("Converting wave to DC")
dc=[]
DC_CENTER=0x8080
DC_THRESHOLD=0x4000
DUMP_WIDTH=16
DUMP_RRANGE=range(DUMP_WIDTH)
DUMP_RANGE=range((FRAMELEN+DUMP_WIDTH-1)//DUMP_WIDTH)
for i in FRANGE:
  dc.append(1 if abs(int.from_bytes(frames[i],byteorder='big',signed=False)-DC_CENTER)>=DC_THRESHOLD else 0)
if moden==2:
  for i in DUMP_RANGE:
    row=""
    for j in DUMP_RRANGE:
      row+=str(dc[i*DUMP_WIDTH+j])
    print(hex(i*DUMP_WIDTH)[2:]+"|"+row)
  exitClean()
# dumpclicks
print("Converting DC to clicks")
clicks=[]
for i in FRANGE:
  if i==0:
    clicks.append(dc[i])
  else:
    clicks.append(1 if dc[i]==1 and dc[i-1]==0 else 0)
if moden==3:
  for i in DUMP_RANGE:
    row=""
    for j in DUMP_RRANGE:
      row+="X" if clicks[i*DUMP_WIDTH+j] else " "
    print(hex(i*DUMP_WIDTH)[2:]+"|"+row)
  exitClean()
# run
OUTEVERY=1 if mode=="rundebug" else 128
PLAYFREQ=60
PLAYPERIOD=1.0/PLAYFREQ
print("Playing back at "+str(PLAYFREQ)+"Hz of "+str(wavefile.getframerate())+"Hz file. Recommended tick rate: "+str(20.0*PLAYFREQ/wavefile.getframerate()))
print("Press enter to start")
input()
for i in range(5,0,-1):
  print(i)
  time.sleep(1)
start_time=time.time()
print(start_time)
clicks_done=0
pyautogui.PAUSE=0
TIMER_EXPERIMENTAL=True
for i in FRANGE:
  if clicks[i]==1:
    if TIMER_EXPERIMENTAL:
      while time.time()-start_time<PLAYPERIOD*i:
        continue
    else:
      now=time.time()
      if now-start_time<PLAYPERIOD*i:
        time.sleep((PLAYPERIOD*i-(now-start_time)))
    pyautogui.click()
    clicks_done+=1
    if clicks_done%OUTEVERY==0 or i==FRAMELEN-1:
      now=time.time()
      print(str(i)+" "+"{:.3f}".format(PLAYPERIOD*i)+" "+"{:.3f}".format(now-start_time)+" "+str(int(((now-start_time)-PLAYPERIOD*i)*1000)))
      if (now-start_time)-PLAYPERIOD*i>PLAYPERIOD*2:
        print("Process lagging: running at "+str(i/(now-start_time))+"Hz")
print("Playback finished. Speed up the footage by x"+str(wavefile.getframerate()/PLAYFREQ)+".")
exitClean()