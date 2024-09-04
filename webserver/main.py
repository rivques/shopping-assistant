import bottle

@bottle.route('/upc2wav/<store>/<upc>')
def upc2wav(store, upc):
    print(f"Got request for {store}/{upc}")
    return "implement me"

@bottle.route('/')
def index():
    return "Try hitting the /upc2wav/<store>/<upc> endpoint"

bottle.run(host='0.0.0.0', port=7467)