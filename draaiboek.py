from tkinter import *
import os

from playsound import playsound


conf = {}
conf['draaiboek']=[]



def play(e):
    current = conf['listbox'].curselection() #selection_get()
    if len(current)!=1:
        print('More than one selected')
        print(current)
        return

    selected = conf['draaiboek'][current[0]]

    if selected["type"]=='PLAY':
        print("playing %s"%selected['file'])
        playsound(selected['file'])


    


def init():
    master = Tk()
    master.title("Draaiboek")
    master.geometry('500x500')

    scrollbar = Scrollbar(master)
    scrollbar.pack( side = 'right', fill = 'both' )

    listbox = Listbox(master, yscrollcommand=scrollbar.set)
    listbox.pack(side="left",fill="both", expand=True)
    scrollbar.config( command = listbox.yview )
    listbox.bind('<Double-1>', play)#lambda x: selectButton.invoke())

    # Read the "program" that we are supposed to do (the draaiboek)
    with open('tsok.txt') as f:
        program = [ p.strip() for p in f.readlines() ]

    draaiboek = []
    for p in program:
        if p.startswith('PLAY'):
            filename = p[4:].strip()
            if not os.path.exists(filename):
                print("# WARNING! File %s does not exist!"%filename)
            draaiboek.append({"type":"PLAY","file":filename})
        else:
            draaiboek.append({"type":"MSG","content":p})
            
        
    for i,schedule in enumerate(draaiboek):
        if schedule["type"]=="PLAY":
            listbox.insert(END,schedule["file"])
            listbox.itemconfig(i, {'fg': 'blue'})
        if schedule["type"]=="MSG":
            listbox.insert(END,schedule["content"])
            listbox.itemconfig(i, {'fg': 'black'})

    conf['listbox']=listbox
    conf['draaiboek']=draaiboek

            

        
init()

mainloop()

