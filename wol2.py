from flask import Flask, render_template_string, request, jsonify
from wakeonlan import send_magic_packet

app = Flask(__name__)

# HTML template for the webpage with a button and a text input
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Wake-on-LAN</title>
    <style>
        .wol-button {
            padding: 20px;
            font-size: 24px;
            cursor: pointer;
        }
        .mac-input {
            padding: 10px;
            font-size: 18px;
        }
    </style>
</head>
<body>
    <input class="mac-input" type="text" id="macAddress" placeholder="Enter MAC Address" />
    <button class="wol-button" onclick="wakeDevice()">Wake Device</button>
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)