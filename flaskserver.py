from flask import Flask, request, jsonify

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
    return jsonify({'status': 'success', 'data': recieved_rssi}), 200

if __name__ == '__main__':
    app.run(host='192.168.68.151', port=8080)

