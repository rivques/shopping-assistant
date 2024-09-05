import dotenv
dotenv.load_dotenv(override=True)
import bottle
import voicelib

@bottle.route('/upc2wav/<store>/<upc>')
def upc2wav(store, upc):
    print(f"Got request for {store}/{upc}")
    voicelib.describe_upc(upc, f"output/{store}_{upc}.wav")
    return bottle.static_file(f"{store}_{upc}.wav", root="output")

@bottle.route('/')
def index():
    return "Try hitting the /upc2wav/<store>/<upc> endpoint"

bottle.run(host='0.0.0.0', port=7467)