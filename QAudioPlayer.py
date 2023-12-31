import os
import VLC
from  QJumpSlider import QJumpSlider
from PyQt6.QtGui import QFont, QMouseEvent
from PyQt6.QtCore import (
    Qt, 
    QSize, 
    QTimer,
    QEvent
)
from PyQt6.QtWidgets import (
    QPushButton, 
    QHBoxLayout, 
    QStyle,
    QSlider,
    QLabel,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)


class AudioPlayer(QWidget):

    def __init__(self, parent=None):
        super(AudioPlayer, self).__init__(parent)
        
        self.vlc_instance = VLC.Instance()
        self.vlc_mediaPlayer = self.vlc_instance.media_player_new()

        btnSize = QSize(16, 16)

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setFixedHeight(24)
        self.playButton.setIconSize(btnSize)
        self.playButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)
        
        self.stopButton = QPushButton()
        self.stopButton.setEnabled(False)
        self.stopButton.setFixedHeight(24)
        self.stopButton.setIconSize(btnSize)
        self.stopButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop))
        self.stopButton.clicked.connect(self.stop)
        
        self.currentPlaybackTimeLabel = QLabel('--:--')
        self.currentPlaybackTimeLabel.setFont(QFont("Noto Sans", 7))
        
        self.durationLabel = QLabel('--:--')
        self.durationLabel.setFont(QFont("Noto Sans", 7))

        self.positionSlider = QJumpSlider(Qt.Orientation.Horizontal)
        self.positionSlider.setMaximum(1000)
        self.positionSlider.sliderMoved.connect(self.setPosition)
        self.positionSlider.pressed.connect(self.setPosition)
        
        self.volumeSlider = QJumpSlider(Qt.Orientation.Horizontal)
        self.volumeSlider.setMaximum(100)
        self.volumeSlider.setValue(self.vlc_mediaPlayer.audio_get_volume())
        self.volumeSlider.valueChanged.connect(self.setVolume)

        self.statusBar = QStatusBar()
        self.statusBar.setFont(QFont("Noto Sans", 7))
        self.statusBar.setFixedHeight(14)

        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(self.currentPlaybackTimeLabel)
        controlLayout.addWidget(self.positionSlider)
        controlLayout.addWidget(self.durationLabel)
        
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.playButton)
        buttonLayout.addWidget(self.stopButton)
        buttonLayout.addWidget(self.volumeSlider, 25)
        
        layout = QVBoxLayout()
        layout.addLayout(controlLayout)
        layout.addLayout(buttonLayout)
        layout.addWidget(self.statusBar)

        self.setLayout(layout)
        
        self.timer = QTimer(self)
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.updateUI)
    
    def setSource(self, filePath):
        if filePath != '':
            self.media = self.vlc_instance.media_new(filePath)
            self.vlc_mediaPlayer.set_media(self.media)
            self.playButton.setEnabled(True)
            self.stopButton.setEnabled(True)
            self.statusBar.showMessage(''.join(os.path.basename(filePath)).split('.')[0])

    def play(self):
        if self.vlc_mediaPlayer.is_playing():
            self.vlc_mediaPlayer.pause()
            self.playButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
            self.isPaused = True
        else:
            self.vlc_mediaPlayer.play()
            self.playButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
            self.timer.start()
            self.isPaused = False
            
    def stop(self):
        self.vlc_mediaPlayer.stop()
        self.playButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause)) 
        self.playButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))      
        self.positionSlider.setValue(self.positionSlider.minimum())

    def setVolume(self, Volume):
        self.vlc_mediaPlayer.audio_set_volume(Volume)
        

    def setPosition(self, position):
        # setting the position to where the slider was dragged
        self.vlc_mediaPlayer.set_position(position / 1000.0)
        # the vlc MediaPlayer needs a float value between 0 and 1, Qt
        # uses integer variables, so you need a factor; the higher the
        # factor, the more precise are the results
        # (1000 should be enough)
        

    def updateUI(self):
        # setting the slider to the desired position
        self.positionSlider.setValue(self.vlc_mediaPlayer.get_position() * 1000)

        if not self.vlc_mediaPlayer.is_playing():
            self.timer.stop()
            if not self.isPaused:
                self.stop()

    def handleError(self):
        self.playButton.setEnabled(False)
        self.statusBar.showMessage("Error: " + self.vlc_mediaPlayer.errorString())
