from pydub import AudioSegment
from pydub.playback import play

sound = AudioSegment.from_mp3('../demo01/files/11582.mp3')
play(sound)