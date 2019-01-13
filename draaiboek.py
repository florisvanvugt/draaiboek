from tkinter import *
from tkinter import filedialog
import os


import time

import audioread
import math
import pyaudio


conf = {}
conf['draaiboek']=[]



def update_current(c):
    conf['listbox'].itemconfig(conf['current'],{'bg':'white','selectbackground':'gray'}) # "remove" previous selection
    conf['listbox'].itemconfig(c,{'bg':'lightgreen','selectbackground':'green'}) # set current selection
    conf['current']=c

    

def formulate_filename(f): #,played=False,duration='-'):
    s = "  ⇨"
    if f['played']: s="  ✔"
    return s+" "+os.path.basename(f['file'])+'   '+f['duration']





def startstop(e):
    """ Toggle between starting or stopping playback. """
    if conf['playing']:
        stop_playing()
    else: # if we're not playing, start playing now!
        conf['playing']=True



def click_start(e):
    """ When we click with the mouse button on an item."""
    itm = conf['listbox'].curselection()
    if len(itm)!=1:
        print("You have to select exactly one item.")
    itm = itm[0]

    is_same = itm==conf['current']
    update_current(itm)
    if is_same: # if we click on the same item
        print("Toggling")
        startstop(e)

    else:
        # If we just clicked on "another" item
        print("Launching!")
        conf['audio']=None # eliminate whatever we were playing, so we can start afresh
        conf['playing']=True # for sure play!



        

def read_new_file():
    # Read in an entire file and put it in the 'audio' key of the configuration, so we can later play it
    todo = conf['draaiboek'][conf['current']]
    if 'file' not in todo: return
    filename = todo['file']
    print("Reading %s"%filename)
    
    bufs = []
    with audioread.audio_open(filename) as f:

        conf['channels']   =f.channels
        conf['samplerate'] =f.samplerate
        conf['duration']   =f.duration
        # TODO: we'll probably want to make sure that these settings
        # match our pyaudio object.
        for buf in f:
            bufs.append(buf)
            
    conf['audio']=bufs



def mark_completed():
    c = conf['current']
    cur = conf['draaiboek'][c]
    cur['played']=True

    lb = conf['listbox']
    lb.delete(c)
    lb.insert(c,formulate_filename(cur))
    



def stop_playing():
    print("Stopping playback")
    if 'stream' in conf and conf['stream']:
        conf['playing']=False
        s = conf['stream']
        s.stop_stream()
        s.close()
    conf['stream']=None
    conf['audio']=None # also discard the audio
    

    

def next_schedule():
    # Jump to the next item on the schedule
    c = conf['current']
    if not c < len(conf['draaiboek']):
        # Cannot advance any further!
        stop_playing()
        return False

    c+=1
    # Go to the next item that is a PLAY or STOP
    while conf['draaiboek'][c]['type'] not in ['PLAY','STOP']:
        c+=1

    is_stop = conf['draaiboek'][c]['type']=='STOP'
        
    update_current(c)
    return not is_stop



def get_duration(f):
    if not os.path.exists(f): return "-"
    dat = audioread.audio_open(f)
    #print(f.channels, f.samplerate, f.duration)
    dur_sec = "%d:%02d"%(math.floor(dat.duration/60),dat.duration%60)#/dat.samplerate
    dat.close()
    return dur_sec #"%s"%(dur_sec)



def init(f):
    master = conf['master']
    master.title("Draaiboek")
    master.geometry('600x600')


    def on_closing():
        conf["active"]=False
    master.protocol("WM_DELETE_WINDOW", on_closing)

    
    scrollbar = Scrollbar(master)
    scrollbar.pack( side = 'right', fill = 'both' )

    listbox = Listbox(master, yscrollcommand=scrollbar.set)
    listbox.configure(font=('Times New Roman',18))
    listbox.pack(side="left",fill="both", expand=True)
    scrollbar.config( command = listbox.yview )
    listbox.bind('<Double-1>', click_start)

    # Read the "program" that we are supposed to do (the draaiboek)
    with open(f) as f:
        program = [ p.strip() for p in f.readlines() ]

    draaiboek = []
    for p in program:
        if p.startswith('PLAY'):
            filename = p[4:].strip()
            draaiboek.append({"type":"PLAY","file":filename,"played":False,'duration':get_duration(filename)})
        elif p.startswith('STOP'):
            draaiboek.append({"type":"STOP"})
        else:
            draaiboek.append({"type":"MSG","content":p})
            

    for i,schedule in enumerate(draaiboek):
        props = {'bg':'white'}
        if schedule["type"]=="PLAY":
            listbox.insert(END,formulate_filename(schedule))
            props['fg']='blue'
            if not os.path.exists(schedule["file"]):
                print("# WARNING! File %s does not exist!"%schedule["file"])
                props['fg']='red'
            listbox.itemconfig(i, props)
        if schedule["type"]=="STOP":
            listbox.insert(END,'⏹')
            props['fg']='red'
            listbox.itemconfig(i, props)
        if schedule["type"]=="MSG":
            listbox.insert(END,"  "+schedule["content"])
            props['fg']='black'
            listbox.itemconfig(i, props)

    conf['listbox']=listbox
    conf['draaiboek']=draaiboek
    conf['master']=master

            



def ensure_stream():
    # Make sure the stream is open

    if not 'stream' in conf or not conf['stream']:

        # open stream based on the wave object which has been input.
        stream = conf['p'].open(format   = pyaudio.paInt16, # according to audioread, this is the format we get the data in
                                channels = conf['channels'],
                                rate     = conf['samplerate'],
                                output   = True)
        conf['stream']=stream

        

def close_stream():
    if 'stream' in conf:
        conf['stream'].close()
    

conf['master'] = Tk()
fn = filedialog.askopenfilename()
if not fn or not len(fn):
    print("You have to select a file.")
    sys.exit(0)
    


# create an audio object
conf['p'] = pyaudio.PyAudio()

    
init(fn)


conf['master'].bind("<space>", click_start)
    
    

conf['active']  = True # whether we keep the window open
conf['playing'] = False # whether we are currently playing something
conf['current'] = 0 # the current item we are playing
while conf["active"]:
    time.sleep(.001)

    do_read = False

    if conf['playing']:

        # Make sure we have something to play
        do_read = False
        if 'audio' not in conf or conf['audio']==None:
            do_read = True # fresh read

        else:
            if len(conf['audio'])==0: # this is if we were just playing something, but now there is nothing left to play
                mark_completed() # mark the current file as being completed
                do_read = next_schedule() # jump to the next item

        # Did we just hit a stop?
        is_stop = conf['draaiboek'][conf['current']]['type']!='PLAY'
        if is_stop:
            stop_playing()
            conf['playing']=False

    if conf['playing']:
        if do_read:
            read_new_file()

        

            

    if conf['playing']: # if we're still in business
        ensure_stream() # ensure that we have a stream open
        # Actually play
        buf = conf['audio'].pop(0) # take the buffer
        conf['stream'].write(buf) # blocking!
    
    conf['master'].update_idletasks()
    conf['master'].update()



conf['p'].terminate()
