from flask import Flask, render_template_string
from wakeonlan import send_magic_packet

app = Flask(__name__)

# HTML template for the webpage with a button
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
    </style>
</head>
<body>
    <button class="wol-button" onclick="wakeDevice()">Wake Device</button>
    <script>
        function wakeDevice() {
            fetch('/wake', {
                method: 'POST'
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
    # Replace '00:00:00:00:00:00' with the MAC address of the device you want to wake
    mac_address = '00:00:00:00:00:00'
    try:
        send_magic_packet(mac_address)
        return {'message': f'Device with MAC {mac_address} should wake up shortly.'}, 200
    except Exception as e:
        return {'message': str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)