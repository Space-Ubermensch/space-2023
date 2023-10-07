# from .audiolazy import str2midi
# from audiolazy import str2midi
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # Cheap hack to make the line below work
from audiolazy import str2midi

from midiutil import MIDIFile
from PIL import Image
import numpy as np

im = Image.open('/content/images.jpeg')

Ncolumns, Nrows = im.size  
grey_im = im.convert('L')  

row=int(Nrows/2)
pixels = [grey_im.getpixel((i,row)) for i in range(Ncolumns)]
buffL=1
buffR=6   
pixels=pixels[buffL:-buffR]
Npix=int(len(pixels))

instrumentName = 'violin'
noteStr = ['E2','F2','G2','A2','B2','C2','D2',
             'E3','F3','G3','A3','B3', 'C3','D3',
             'E4','F4','G4','A4','B4', 'C4','D4',
             'E5','F5','G5','A5','B5', 'C5','D5']
vmin,vmax=30,120
bpm=137.0625
subDiv = 1./4


def data2notes(yi):
    '''converts normalized y data to quantized midi notes'''
    if yi>ymin:
        data_note_i=int((yi-ymin)/(1.-ymin)*(Nnotes-1))
        return noteMidi[data_note_i]
    else:
        return -1 
def data2vels(yi):
    '''converts normalized y data to quantized note velocities'''
    if yi>ymin:
        data_vels = int(vmin + (yi-ymin)/(1.-ymin)*(vmax-vmin))
        return data_vels
    else:
        return -1  

noteMidi=[str2midi(n) for n in noteStr] 
Nnotes=len(noteMidi)

nBeats = Npix*subDiv       
duration = nBeats/bpm*60.  
print('bpm = {0}, subdivision = {1}, duration = {2} seconds'.format(bpm,subDiv,duration))

time = np.array(range(Npix))*subDiv       
yShift = np.array(pixels)-np.min(pixels)  
scale=2. 
yScale = np.array(yShift)**scale
y = yScale/np.max(yScale)
ymin=0.1


y_notes = [data2notes(yi) for yi in y]
y_vel = [data2vels(yi) for yi in y]

midifile = MIDIFile(adjust_origin=True)
midifile.addTempo(track=0, time=time[0], tempo=bpm)

for i,ti in enumerate(time):
    if y_notes[i]>0:
        midifile.addNote(track=0, channel=0, pitch=y_notes[i], time=ti, duration=subDiv, volume=y_vel[i])

with open("./imported_audio_second8""_violin"+".mid", "wb") as f:
    midifile.writeFile(f)