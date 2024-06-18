from flask import Flask, request, jsonify, render_template
import numpy as np
pi_locations = {1: [0.910, -0.910, 0.333], 
                2 : [0.450, 0.490, -0.350], 
                3 : [-0.846, 0.407, 0.050], 
                4 : [-0.900, -0.900, -0.500]}

MAXINCHES = 156

def regression(data): #TO-DO

    xdata = [v[0] for v in pi_locations.values()] #
    ydata = [v[1] for v in pi_locations.values()] #
    zdata = [v[2] for v in pi_locations.values()] #

    

    distdata = []
    bvectdata = []
    #However the data is formatted CHANGE THIS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    
    #print(data)
    for key in data.keys():

        loc = pi_locations[key]
        a = loc[0]
        b = loc[1]
        c = loc[2]
        d = convert_meters_to_webGL(data[key])
        #d = data[key]

        distdata.append(d)

        bvectdata.append(d ** 2 - c ** 2 - b ** 2 - a ** 2)
    #However the data is formatted CHANGE THIS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    Bdata = [-2 * x for x in xdata]
    Cdata = [-2 * y for y in ydata]
    Ddata = [-2 * z for z in zdata]

    one = np.ones(len(xdata), dtype=float)
    M = np.array([one, Bdata, Cdata, Ddata])
    y = np.array(bvectdata)
    y = y.transpose()  # vertical
    M = M.transpose()  # vertical
    try:
        N = np.linalg.solve(M, y)
    except:
        K = np.linalg.pinv(M)
        N = K @ y


    def eval_error():
        return np.linalg.norm(M @ N - y) ** 2

    return [N[1], N[2], N[3], eval_error()]

def convert_meters_to_webGL(dist):
    dist_inches =  39.3701 * dist
    return dist_inches / MAXINCHES * 2

app = Flask(__name__,
            static_url_path='', 
            static_folder='templates')

recieved_rssi = dict()

@app.route('/reportBLE', methods=['POST'])
def receive_rssi_data():

    data = request.json

    if not 'rssi_values' in data:
        return jsonify({'status': 'error', 'message': 'no rssi', 'data': data}), 400
    
    if not 'ID' in data:
        print(data)
        return jsonify({'status': 'error', 'message': 'no ID', 'data': data}), 400

    rssi_values = data['rssi_values']
    id = data['ID']
    print(f"Received RSSI values from pi {id}: {rssi_values}")

    # Add logic to handle the received data as needed
    recieved_rssi[id] = rssi_values
    
    return jsonify({'status': 'success', 'data': rssi_values}), 200


@app.route('/getData', methods=['GET'])
def get_data():
    # test = {
    #     1: 1.28,
    #     2: 1.05,
    #     3: 1.82,
    #     4: 2.44
    # }
    # regression_result = regression(test)

    regression_result = regression(recieved_rssi)
    return jsonify({'status': 'success', 'data': regression_result}), 200


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host="192.168.68.103", port=8080)

