import time

from modelscope.outputs import OutputKeys
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
from pydub.playback import play

import io

from pydub import AudioSegment



text = ('<speak><emotion category="hate" intensity="1.0">你要上天了！</emotion></speak>', '你要上天了！')
model_id = 'damo/speech_sambert-hifigan_tts_zhiyan_emo_zh-cn_16k'
sambert_hifigan_tts = pipeline(task=Tasks.text_to_speech, model=model_id)


for x in text:
    start = time.time()
    output = sambert_hifigan_tts(input=x)
    wav = output[OutputKeys.OUTPUT_WAV]
    song = AudioSegment.from_file(io.BytesIO(wav), format="wav")
    print(time.time() - start)

    play(song)