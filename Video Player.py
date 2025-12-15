import sys,os
from PyQt5 import QtWidgets,QtCore,QtGui
import vlc
class VideoPlayer(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Local Video Player")
        self.setGeometry(200,100,1000,620)
        self.instance=vlc.Instance()
        self.player=self.instance.media_player_new()
        self.is_paused=False
        self.build_ui()
        self.setup_timer()
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
    def build_ui(self):
        self.videoframe=QtWidgets.QFrame()
        self.videoframe.setStyleSheet("background:black;")
        self.openbtn=QtWidgets.QPushButton("Open")
        self.playbtn=QtWidgets.QPushButton("Play")
        self.stopbtn=QtWidgets.QPushButton("Stop")
        self.time_label=QtWidgets.QLabel("00:00 / 00:00")
        self.position_slider=QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.position_slider.setRange(0,1000)
        self.position_slider.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents,True)
        self.position_slider.setFocusPolicy(QtCore.Qt.NoFocus)
        self.volume_slider=QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.volume_slider.setRange(0,100)
        self.volume_slider.setValue(80)
        self.mutebtn=QtWidgets.QPushButton("Mute")
        layout=QtWidgets.QVBoxLayout()
        layout.addWidget(self.videoframe,stretch=8)
        layout.addWidget(self.position_slider)
        bottom=QtWidgets.QHBoxLayout()
        bottom.addWidget(self.time_label)
        bottom.addStretch()
        bottom.addWidget(self.openbtn)
        bottom.addWidget(self.playbtn)
        bottom.addWidget(self.stopbtn)
        bottom.addWidget(self.mutebtn)
        bottom.addWidget(QtWidgets.QLabel("Vol"))
        bottom.addWidget(self.volume_slider)
        layout.addLayout(bottom)
        self.setLayout(layout)
        self.openbtn.clicked.connect(self.open_file)
        self.playbtn.clicked.connect(self.play_pause)
        self.stopbtn.clicked.connect(self.stop)
        self.mutebtn.clicked.connect(self.toggle_mute)
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.player.audio_set_volume(self.volume_slider.value())
    def setup_timer(self):
        self.timer=QtCore.QTimer(self)
        self.timer.setInterval(300)
        self.timer.timeout.connect(self.update_ui)
        self.timer.start()
    def open_file(self):
        path,_=QtWidgets.QFileDialog.getOpenFileName(self,"Open Video",os.path.expanduser("~"))
        if not path: return
        media=self.instance.media_new(path)
        self.player.set_media(media)
        self.set_video_handle()
        self.player.play()
        self.playbtn.setText("Pause")
        self.is_paused=False
    def play_pause(self):
        if self.player.is_playing():
            self.player.pause()
            self.is_paused=True
            self.playbtn.setText("Play")
        else:
            self.player.play()
            self.is_paused=False
            self.playbtn.setText("Pause")
    def stop(self):
        self.player.stop()
        self.playbtn.setText("Play")
    def keyPressEvent(self,event):
        k=event.key()
        if k==QtCore.Qt.Key_Space:
            self.play_pause()
            event.accept()
            return
        if k==QtCore.Qt.Key_Left:
            self.skip_seconds(-10)
            event.accept()
            return
        if k==QtCore.Qt.Key_Right:
            self.skip_seconds(10)
            event.accept()
            return
        super().keyPressEvent(event)
    def skip_seconds(self,s):
        cur=self.player.get_time()
        if cur is None or cur<0:
            return
        new=cur+int(s*1000)
        if new<0: new=0
        length=self.player.get_length()
        if length>0 and new>length: new=length-100
        self.player.set_time(new)
    def update_ui(self):
        length=self.player.get_length()
        pos=self.player.get_time()
        if length>0 and pos>=0:
            frac=pos/length
            self.position_slider.blockSignals(True)
            self.position_slider.setValue(int(frac*1000))
            self.position_slider.blockSignals(False)
            self.time_label.setText(f"{self.ms_to_hms(pos)} / {self.ms_to_hms(length)}")
        else:
            self.time_label.setText("00:00 / 00:00")
    def ms_to_hms(self,ms):
        if ms is None or ms<=0: return "00:00"
        s=int(ms/1000)
        h=s//3600
        m=(s%3600)//60
        sec=s%60
        if h>0: return f"{h:02d}:{m:02d}:{sec:02d}"
        return f"{m:02d}:{sec:02d}"
    def set_video_handle(self):
        if sys.platform.startswith("linux"):
            self.player.set_xwindow(self.videoframe.winId())
        elif sys.platform=="win32":
            self.player.set_hwnd(self.videoframe.winId())
        elif sys.platform=="darwin":
            self.player.set_nsobject(int(self.videoframe.winId()))
    def toggle_mute(self):
        muted=self.player.audio_get_mute()
        self.player.audio_set_mute(not muted)
        self.mutebtn.setText("Unmute" if not muted else "Mute")
    def set_volume(self,v):
        self.player.audio_set_volume(int(v))
    def showEvent(self,e):
        super().showEvent(e)
        self.setFocus()
if __name__=="__main__":
    app=QtWidgets.QApplication(sys.argv)
    player=VideoPlayer()
    player.show()
    sys.exit(app.exec_())
