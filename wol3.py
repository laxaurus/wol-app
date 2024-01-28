"""
This program is a Python-based web application using Flask, a lightweight web framework, which provides two main functionalities:

    Wake-on-LAN (WOL): It serves a web page that allows users to input a MAC address and then click a "Wake Device" button to send a WOL packet to the specified device. The wake-on-LAN routine is triggered via a POST request to the /wake endpoint, which uses the send_magic_packet function from the wakeonlan library to attempt to wake the device with the provided MAC address.

    Ping Status Check: The web page also includes a "Check Status" button. When clicked, it triggers a JavaScript function that sends a POST request to the /status endpoint with an IP address. The server-side route for /status uses the ping3 library to send an ICMP echo request (ping) to the provided IP address. The response from the ping determines whether the device is up (responding) or down (not responding).

Both buttons are part of a simple HTML webpage with JavaScript functions that handle the button clicks and the asynchronous requests to the server. The Flask application handles these requests, executes the WOL or ping operations, and returns JSON responses indicating the success or failure of the requested action, along with an appropriate message.

The application is intended to run on a local network where WOL and ICMP are permitted, and the target devices are configured to respond to these protocols. It allows users to remotely wake devices and check their online status through a simple web interface.

"""


from flask import Flask, render_template_string, request, jsonify
from wakeonlan import send_magic_packet
from ping3 import ping

app = Flask(__name__)


# HTML template for the webpage with two buttons and a text input
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Wake-on-LAN and Ping Status</title>
    <style>
        .button {
            padding: 20px;
            font-size: 24px;
            margin: 10px;
            cursor: pointer;
        }
        .mac-input {
            padding: 10px;
            font-size: 18px;
            margin: 10px;
        }
        .ip-input {
            padding: 10px;
            font-size: 18px;
            margin: 10px;
        }        
    </style>
</head>
<body>
    <input class="mac-input" type="text" id="macAddress" placeholder="Enter MAC Address" />
    <button class="button" onclick="wakeDevice()">Wake Device</button>
    <input class="ip-input" type="text" id="ipAddress" placeholder="Enter IP Address" />
    <button class="button" onclick="checkStatus()">Check Status</button>
    <script>
        function wakeDevice() {
            var mac = document.getElementById('macAddress').value;
            fetch('/wake', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ mac_address: mac })
            }).then(response => response.json())
            .then(data => {
                alert(data.message);
            });
        }
        
        function checkStatus() {
            var ip = document.getElementById('ipAddress').value;
            fetch('/status', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ ip_address: ip })
            }).then(response => response.json())
            .then(data => {
                alert(data.message);
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(html_template)

@app.route('/wake', methods=['POST'])
def wake():
    data = request.get_json()
    mac_address = data.get('mac_address')
    
    if not mac_address:
        return jsonify({'message': 'MAC address is missing!'}), 400

    try:
        send_magic_packet(mac_address)
        return jsonify({'message': f'Device with MAC {mac_address} should wake up shortly.'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/status', methods=['POST'])
def status():
    data = request.get_json()
    ip_address = data.get('ip_address')
    
    if not ip_address:
        return jsonify({'message': 'IP address is missing!'}), 400
    
    response = ping(ip_address, timeout=2)
    
    if response is not None:
        return jsonify({'message': f'Device with IP {ip_address} is up. Response time: {response} seconds.'}), 200
    else:
        return jsonify({'message': f'Device with IP {ip_address} is down or not reachable.'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)