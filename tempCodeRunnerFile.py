import os
import pickle
import tkinter as tk
from mutagen.mp3 import MP3
from tkinter import filedialog
from tkinter import PhotoImage
from pygame import mixer


class Player(tk.Frame):
	def __init__(self, master=None):
		super().__init__(master)
		self.master = master
		self.pack()
		mixer.init()

		if os.path.exists('songs.pickle'):
			with open('songs.pickle', 'rb') as f:
				self.playlist = pickle.load(f)
		else:
			self.playlist=[]

		self.current = 0
		self.paused = True
		self.played = False

		self.create_frames()
		self.track_widgets()
		self.control_widgets()
		self.tracklist_widgets()
       
		self.master.bind('<Left>', self.prev_song)
		self.master.bind('<space>', self.play_pause_song)
		self.master.bind('<Right>', self.next_song)
    
	def create_frames(self):
#songtrack frame 1
		self.track = tk.LabelFrame(self, text='Song Track', 
					font=("times new roman",15,"bold"),
					bg="grey",fg="black",bd=5,relief=tk.GROOVE)
		self.track.config(width=450,height=350) 
		self.track.grid(row=0, column=0, padx=8,pady=10)
#--------------------------------------------------------------------------------------------------------------
#plalist frame2
		self.tracklist = tk.LabelFrame(self, text=f'PlayList - {str(len(self.playlist))}',
							font=("times new roman",15,"bold"),
							bg="grey",fg="black",bd=5,relief=tk.GROOVE)
		self.tracklist.config(width=190,height=350)
		self.tracklist.grid(row=0, column=1, rowspan=3, pady=9,padx=5)
#---------------------------------------------------------------------------------------------------------------
#button controls frame 3
		self.controls = tk.LabelFrame(self,
							font=("times new roman",15,"bold"),
							bg="light blue",fg="black",bd=7,relief=tk.GROOVE)
		self.controls.config(width=410,height=150)
		self.controls.grid(row=2, column=0, pady=1, padx=2)
#---------------------------------------------------------------------------------------------------------------
	def track_widgets(self):
		self.canvas = tk.Label(self.track, image=img,bg="red")
		self.canvas.configure(width=550, height=320)
		self.canvas.grid(row=0,column=0)

		self.songtrack = tk.Label(self.track, font=("times new roman",16,"bold"),
						bg="white",fg="dark blue")
		self.songtrack['text'] = '<-----------GROOVE_MP3_Player------------>'
		self.songtrack.config(width=40, height=1,bg="light yellow")
		self.songtrack.grid(row=1,column=0,padx=10)

	def control_widgets(self):
		self.loadSongs = tk.Button(self.controls, bg='green', fg='white', font=20,width=13, height=2)
		self.loadSongs['text'] = 'Load Songs'
		self.loadSongs['command'] = self.retrieve_songs
		self.loadSongs.grid(row=0, column=0, padx=10)

		self.prev = tk.Button(self.controls, image=prev, width=46, height=45,bg='yellow')
		self.prev['command'] = self.prev_song
		self.prev.grid(row=0, column=1, padx=5,pady=10)

		self.pause = tk.Button(self.controls, image=pause, width=60, height=55,bg='yellow')
		self.pause['command'] = self.pause_song
		self.pause.grid(row=0, column=2,padx=5,pady=5)

		self.next = tk.Button(self.controls, image=next_ , width=46, height=45,bg='yellow')
		self.next['command'] = self.next_song
		self.next.grid(row=0, column=3, padx=5,pady=10)

		self.volume = tk.DoubleVar(self)
		self.slider = tk.Scale(self.controls, from_ = 0, to = 15, orient = tk.HORIZONTAL, width=20,len=180,bg='white')
		self.slider['variable'] = self.volume
		self.slider.set(5)
		mixer.music.set_volume(0.5)
		self.slider['command'] = self.change_volume
		self.slider.grid(row=0, column=4, padx=10)


	def tracklist_widgets(self):
		self.scrollbar = tk.Scrollbar(self.tracklist, orient=tk.VERTICAL)
		self.scrollbar.grid(row=0,column=1, rowspan=5, sticky='ns')

		self.list = tk.Listbox(self.tracklist, selectmode=tk.SINGLE,
					 yscrollcommand=self.scrollbar.set, selectbackground='sky blue')
		self.enumerate_songs()
		self.list.config(height=26,width=40,bg="light yellow")
		self.list.bind('<Double-1>', self.play_song) 

		self.scrollbar.config(command=self.list.yview)
		self.list.grid(row=0, column=0, rowspan=5,pady=12)

	def retrieve_songs(self):
		self.songlist = []
		directory = filedialog.askdirectory()
		for root_, dirs, files in os.walk(directory):
				for file in files:
					if os.path.splitext(file)[1] == '.mp3':
						path = (root_ + '/' + file).replace('\\','/')
						self.songlist.append(path)

		with open('songs.pickle', 'wb') as f:
			pickle.dump(self.songlist, f)
		self.playlist = self.songlist
		self.tracklist['text'] = f'PlayList - {str(len(self.playlist))}'
		self.list.delete(0, tk.END)
		self.enumerate_songs()

	def enumerate_songs(self):
		for index, song in enumerate(self.playlist):
			self.list.insert(index, os.path.basename(song))

	def play_pause_song(self, event):
		if self.paused:
			self.play_song()
		else:
			self.pause_song()
   
    
	def play_song(self, event=None):
		if event is not None:
			self.current = self.list.curselection()[0]
			for i in range(len(self.playlist)):
				self.list.itemconfigure(i, bg="white")

		print(self.playlist[self.current])
		mixer.music.load(self.playlist[self.current])
		self.songtrack['anchor'] = 'w'
		self.songtrack['text'] = os.path.basename(self.playlist[self.current])

		# Retrieve song running time
		audio = MP3(self.playlist[self.current])
		song_length = int(audio.info.length)
		minutes, seconds = divmod(song_length, 60)
		song_length_formatted = "{:02d}:{:02d}".format(minutes, seconds)
		
		# Append song runtime to the label text
		self.songtrack['text'] += f" - {song_length_formatted}"

		self.pause['image'] = play
		self.paused = False
		self.played = True
		self.list.activate(self.current)
		self.list.itemconfigure(self.current, bg='sky blue')

		mixer.music.play()

	def pause_song(self):
		if not self.paused:
			self.paused = True
			mixer.music.pause()
			self.pause['image'] = pause
		else:
			if self.played == False:
				self.play_song()
			self.paused = False
			mixer.music.unpause()
			self.pause['image'] = play

	def prev_song(self, event=None):
		self.master.focus_set()
		if self.current > 0:
			self.current -= 1
		else:
			self.current = 0
		self.list.itemconfigure(self.current + 1, bg='white')
		self.play_song()

	def next_song(self, event=None):
		self.master.focus_set()
		if self.current < len(self.playlist) - 1:
			self.current += 1
		else:
			self.current = 0
		self.list.itemconfigure(self.current - 1, bg='white')
		self.play_song()

	def change_volume(self, event=None):
		self.v = self.volume.get()
		mixer.music.set_volume(self.v / 10)

# ----------------------------- Main ------------------------------------------
if __name__ == '__main__':
	root = tk.Tk()
	root.geometry('900x520')
	root.title('GROOVE')
	root.configure(bg='grey')
		
	img = PhotoImage(file='icons/music.gif')
	next_ = PhotoImage(file = 'icons/next.gif')
	prev = PhotoImage(file='icons/previous.gif')
	play = PhotoImage(file='icons/play.gif')
	pause = PhotoImage(file='icons/pause.gif')

	app = Player(master=root)
	app.mainloop()