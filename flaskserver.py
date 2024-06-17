from flask import Flask, request, jsonify, render_template
import numpy as np
pilocations = {"Device1": [.02, .02, .02], "Device2" : [.03, .03, .03], "Device3" : [.04, .04, .04], "Device4" : [.05, .05, .05]}



def regression(rssi): #TO-DO
    xdata = pilocations[] #
    ydata = pilocations[] #
    zdata = pilocations[] #

    Bdata = []
    Cdata = []
    Ddata = []

    distdata = []
    bvectdata = []
    #However the data is formatted CHANGE THIS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    
    #print(data)
    for i in range(len(data)):
    datapoint = data[i].split(" ")
    a = float(datapoint[0])
    b = float(datapoint[1])
    c = float(datapoint[2])
    d = float(datapoint[3])
    xdata.append(a)
    ydata.append(b)
    zdata.append(c)
    Bdata.append(-2 * a)
    Cdata.append(-2 * b)
    Ddata.append(-2 * c)
    distdata.append(d)
    bvectdata.append(d ** 2 - c ** 2 - b ** 2 - a ** 2)
    #However the data is formatted CHANGE THIS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


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



app = Flask(__name__)

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
    regression_result = regression(recieved_rssi)
    return jsonify({'status': 'success', 'data': regression_result}), 200


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='192.168.68.151', port=8080)

