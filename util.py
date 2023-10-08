# from .audiolazy import str2midi
# from audiolazy import str2midi
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # Cheap hack to make the line below work
from audiolazy import str2midi

from midiutil import MIDIFile
from PIL import Image
import numpy as np
from moviepy.editor import *
import moviepy.editor as mp
import cv2
from midi2audio import FluidSynth

class Sonify:
    def __init__(image=None, soundfont_path=None)):
        self.im = image
        self.midipath = './generated_midi.mid' 
        self.audio = './generated_audio.mp3' 
        self.soundfont_path = soundfont_path 
        self.output_video_path = './generated_audio.mp4'
        self.audio_duration = None 
    def run(self):
        try:
            self.generate_midi()
            self.midi_to_audio()
            self.generate_raw_video()
            self.decorate_video()
            return 0
        except Exception as e:
            print(e)
            return
    def generate_midi(self): 
        im = Image.open(self.im)
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
        self.duration = duration
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

        with open(self.midipath, "wb") as f:
            midifile.writeFile(f)
    def midi_to_audio(self):

        # Create a FluidSynth instance with the specified soundfont
        fs = FluidSynth(self.soundfont_file)

        # Convert MIDI to WAV (temporary)
        temp_wav = 'temp.wav'
        fs.midi_to_audio(self.midipath, temp_wav)

        # Convert WAV to MP3 using an external tool like FFmpeg
        os.system(f'ffmpeg -i {temp_wav} {self.audio}')
        # Remove the temporary WAV file
        os.remove(temp_wav)

        # print(f'Conversion completed: {output_mp3}')
    def generate_raw_video(self):
        duration = self.audio_duration# Change this to your desired duration
        # Create a single frame from an image
        image_path = self.im 
        img = ImageClip(image_path, duration=duration)

        # Create a video with the single frame
        video = img.to_videofile(self.video_path, codec='libx264', fps=24)

    def decorate_video(self):
        video_capture = cv2.VideoCapture(self.video_path)
        h = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        w = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        video_capture.release()
        video_clip = mp.VideoFileClip(self.output_video_path)

        # Get the duration of the video in seconds
        video_duration = video_clip.duration

        # Create a function to generate frames for the progress bar overlay
        def add_progress_bar(get_frame, t):
            progress = t / video_duration
            progress_percentage = int(progress * 100)

            # Create a progress bar image (customize the appearance as needed)
            w, h = video_clip.size
            progress_bar_color = (0, 255, 0)  # Green color for the progress bar
            progress_bar_height = h  # Height of the progress bar matches the video height
            progress_bar_width = 1
            progress_bar_x = int(progress * w)

            frame = video_clip.get_frame(t)
            frame_mut = np.array(frame)
            frame_mut[h - progress_bar_height:, progress_bar_x:progress_bar_x + progress_bar_width] = progress_bar_color

            return frame_mut

        # Create a new video with the progress bar overlay
        progress_video = mp.VideoClip(lambda t: add_progress_bar(video_clip.get_frame, t), duration=video_duration)

        # Load the audio clip
        audio_clip = mp.AudioFileClip(self.audio)

        # Set the audio for the progress video
        progress_video = progress_video.set_audio(audio_clip)

        # Write the final video with the progress bar overlay and audio
        progress_video.write_videofile(self.output_video_path, codec="libx264", audio_codec="aac", fps=24)
