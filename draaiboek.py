from tkinter import *
from tkinter import filedialog
from tkinter import ttk
import os


import time

import audioread
import math
import pyaudio


conf = {}
conf['draaiboek']=[]





# The resolution of the progress bar
PROGRESS_RES = 500

def update_progress_bar():
    """ Update the progress bar to reflect how far we are in the current playback."""
    if 'audio' not in conf or not conf['audio'] or 'nbuf' not in conf:
        conf['progress']['value']=0
        return
    nleft = len(conf['audio']) # how many buffers are left
    tot = conf['nbuf']
    p = int( float(PROGRESS_RES)*(tot-nleft) / tot )
    conf['progress']['value']=p


def update_current(c):
    """ Switch the currently active item in the schedule. """
    conf['listbox'].itemconfig(conf['current'],{'bg':'white','selectbackground':'gray'}) # "remove" previous selection
    conf['listbox'].itemconfig(c,{'bg':'lightgreen','selectbackground':'green'}) # set current selection

    conf['listbox'].selection_clear(0, END)
    conf['listbox'].selection_set(c)
    conf['listbox'].activate(c)
    conf['listbox'].focus()

    
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
        #print("Toggling")
        startstop(e)

    else:
        # If we just clicked on "another" item
        #print("Launching!")
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

        if conf['channels']!=f.channels or conf['samplerate']!=f.samplerate:
            # we have to close and re-open the audio output, because otherwise we're playing at the wrong sampling rate
            conf['restart.stream']=True
            
        conf['channels']   =f.channels
        conf['samplerate'] =f.samplerate
        #conf['duration']   =f.duration
        # TODO: we'll probably want to make sure that these settings
        # match our pyaudio object.
        for buf in f:
            bufs.append(buf)
            
    conf['audio']=bufs
    conf['nbuf']=len(bufs)



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



def init(fname):

    # Build the interface
    master = conf['master']
    master.title("Draaiboek")
    master.geometry('600x600')

    master.style = ttk.Style()
    master.style.theme_use("default")

    def on_closing():
        conf["active"]=False
    master.protocol("WM_DELETE_WINDOW", on_closing)


    f = Frame(master)
    scrollbar = Scrollbar(f)
    scrollbar.pack( side = 'right', fill = 'both' )

    listbox = Listbox(f, yscrollcommand=scrollbar.set)
    listbox.configure(font=('Times New Roman',18))
    listbox.pack(side="top",fill="both", expand=True)
    scrollbar.config( command = listbox.yview )
    listbox.bind('<Double-1>', click_start)
    f.pack(side='top',fill='both',expand=True)


    f = Frame(master)
    f.pack(side='bottom',fill=X)

    statusv = StringVar()
    statusv.set('Ready')
    w = Label(f, textvariable=statusv)
    w.pack(side='right',expand=False)
    conf['status']=statusv

    progress = ttk.Progressbar(f, orient=HORIZONTAL,
                               maximum=PROGRESS_RES,
                               mode='determinate')
    progress.pack(side='left',expand=True,fill=X)

    # Read the "program" that we are supposed to do (the draaiboek)
    with open(fname) as f:
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
            cont = schedule['content']
            if cont.endswith('.m4a'):
                cont = cont[:-4]
            listbox.insert(END,"  "+cont)
            props['fg']='black'
            if schedule["content"].startswith('#'):
                props['fg']='gray'
            listbox.itemconfig(i, props)


    conf['master'].bind("<space>", click_start)

    conf['listbox']=listbox
    conf['draaiboek']=draaiboek
    conf['progress']=progress
    conf['master']=master

            



def ensure_stream():
    # Make sure the stream is open

    if 'restart.stream' in conf and conf['restart.stream']:
        print("Restarting stream because requested to do so. Probably because we start playing a file with different stream parameters.")
        close_stream()
        conf['restart.stream']=False
    
    
    if not 'stream' in conf or not conf['stream']:

        # open stream based on the wave object which has been input.
        stream = conf['p'].open(format   = pyaudio.paInt16, # according to audioread, this is the format we get the data in
                                channels = conf['channels'],
                                rate     = conf['samplerate'],
                                output   = True)
        conf['stream']=stream

        

def close_stream():
    if 'stream' in conf and conf['stream']:
        conf['stream'].close()
    



        
conf['master'] = Tk()
fn = filedialog.askopenfilename()
if not fn or not len(fn):
    print("You have to select a file.")
    sys.exit(0)
    


# create an audio object
conf['p'] = pyaudio.PyAudio()


# initialise the interface
init(fn)


    
    

conf['active']  = True # whether we keep the window open
conf['playing'] = False # whether we are currently playing something
conf['current'] = 0 # the current item we are playing
conf['channels']   = 0 
conf['samplerate'] = 0
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
        if conf['stream']:# and conf['stream'].is_active():
            buf = conf['audio'].pop(0) # take the buffer
            try:
                conf['stream'].write(buf) # blocking!
            except:
                print("## Problem writing to stream!")
                #print(e)
        else:
            print("## WARNING: trying to play but the stream is not open!")

        update_progress_bar()


    status = 'Playing' if conf['playing'] else 'Ready'
    conf['status'].set(status)
    
    
    conf['master'].update_idletasks()
    conf['master'].update()



conf['p'].terminate()
