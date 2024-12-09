import os
import time
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

@bottle.route('/upc2mp3sync/<store>/<upc>')
def upc2mp3sync(store, upc):
    print(f"Got sync MP3 request for {store}/{upc}")
    wavpath = f"output/{store}_{upc}.wav"
    mp3path = f"output/{store}_{upc}.mp3"
    text_description = voicelib.describe_upc(upc)
    voicelib.text_to_wav(text_description, wavpath)
    voicelib.wav_to_mp3(wavpath, mp3path)
    return bottle.static_file(mp3path, root='.')

@bottle.route('/upc2mp3/<store>/<upc>')
def upc2mp3(store, upc):
    cached_file = check_cache(store, upc)
    if cached_file:
        print(f"Got cached MP3 request for {store}/{upc}")
        return bottle.static_file(cached_file, root='.')

    # like sync, but it streams the llm response
    print(f"Got streamed MP3 request for {store}/{upc}")
    wavpath = f"output/{store}_{upc}.wav"
    mp3path = f"output/{store}_{upc}.mp3"
    oai_response = voicelib.describe_upc_streamed(upc)
    if not oai_response:
        print("Product not found")
        return bottle.static_file("not_found.mp3", root='.')
    for chunk in oai_response:
        if chunk.choices[0].delta.content:
            print(f"Got text chunk {chunk.choices[0].delta.content}")
            voicelib.streamed_text_to_wav(chunk.choices[0].delta.content, wavpath)
        else:
            print("got other chunk:")
            print(chunk)
    print("Finalizing stream")
    voicelib.streamed_text_finalize(wavpath)
    voicelib.wav_to_mp3(wavpath, mp3path)
    return bottle.static_file(mp3path, root='.')

def check_cache(store, upc):
    mp3path = f"output/{store}_{upc}.mp3"
    if os.path.isfile(mp3path):
        # regenerate the file if it's older than a week
        if os.path.getmtime(mp3path) < time.time() - 60 * 60 * 24 * 7:
            print(f"Cache file {mp3path} is older than a week, regenerating")
            return None
        return mp3path
    return None

@bottle.route('/')
def index():
    return "Try hitting the /upc2mp3/&lt;store&gt;/&lt;upc&gt; endpoint"

bottle.run(host='0.0.0.0', port=7467)