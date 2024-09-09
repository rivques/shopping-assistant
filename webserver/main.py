import dotenv
dotenv.load_dotenv(override=True)
import bottle
import voicelib

@bottle.route('/upc2txt/<store>/<upc>')
def upc2txt(store, upc):
    print(f"Got TXT request for {store}/{upc}")
    return voicelib.describe_upc(upc)

@bottle.route('/upc2wav/<store>/<upc>')
def upc2wav(store, upc):
    print(f"Got WAV request for {store}/{upc}")
    wavpath = f"output/{store}_{upc}.wav"
    text_description = voicelib.describe_upc(upc)
    voicelib.text_to_wav(text_description, wavpath)
    return bottle.static_file(wavpath, root='.')

@bottle.route('/upc2mp3/<store>/<upc>')
def upc2mp3(store, upc):
    print(f"Got MP3 request for {store}/{upc}")
    wavpath = f"output/{store}_{upc}.wav"
    mp3path = f"output/{store}_{upc}.mp3"
    text_description = voicelib.describe_upc(upc)
    voicelib.text_to_wav(text_description, wavpath)
    voicelib.wav_to_mp3(wavpath, mp3path)
    return bottle.static_file(mp3path, root='.')

@bottle.route('/')
def index():
    return "Try hitting the /upc2wav/<store>/<upc> endpoint"

bottle.run(host='0.0.0.0', port=7467)