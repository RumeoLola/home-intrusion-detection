from gpiozero import MotionSensor, Buzzer
from flask import Flask, jsonify, request, redirect, url_for
import threading

# Flask app setup
app = Flask(__name__)

# Initialize GPIO components
pir = MotionSensor(4)  # Motion sensor connected to GPIO pin 4
buzzer = Buzzer(17)    # Piezo buzzer connected to GPIO pin 17

motion_data = "No motion detected"  # Initial motion status
manual_buzzer_control = False       # Flag for manual control of the buzzer

# Function to continuously update motion detection status
def update_motion_data():
    global motion_data, manual_buzzer_control
    while True:
        try:
            # Wait for motion detection
            pir.wait_for_motion()
            print("Motion detected")
            motion_data = "Motion detected"
            # Turn on the buzzer if not manually controlled
            if not manual_buzzer_control:
                buzzer.on()
            
            # Wait for no motion
            pir.wait_for_no_motion()
            print("No motion detected")
            motion_data = "No motion detected"
            # Turn off the buzzer if not manually controlled
            if not manual_buzzer_control:
                buzzer.off()
        
        except Exception as e:
            print(f"Error in motion detection: {e}")

# HTML template as a multi-line string
html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Motion Sensor Status</title>
    <style>
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            flex-direction: column;
            background-color: #f0f0f0;
        }
        p {
            background-color: green;
            width: 150px;
            height: 50px;
            color: white;
            text-align: center;
            line-height: 50px; /* vertically center text */
            font-weight: bold;
            margin-bottom: 20px;
        }
        button {
            background-color: blue;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            margin: 5px;
            cursor: pointer;
        }
        button:hover {
            background-color: darkblue;
        }
    </style>
</head>
<body>
    <p id="motionStatus">No motion detected</p>
    <form method="POST" action="/control">
        <button type="submit" name="action" value="stop">Stop alarm</button>
        <button type="submit" name="action" value="start">Start alarm</button>
    </form>
    <script>
        function fetchMotionData() {
            fetch('/data')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('motionStatus').innerText = data.motion_status;
                });
        }
        setInterval(fetchMotionData, 1000); // Fetch data every second
    </script>
</body>
</html>
'''

# Flask route for the home page, returns the HTML template
@app.route('/')
def index():
    return html_template

# Flask route to return motion detection status as JSON
@app.route('/data')
def data():
    return jsonify({'motion_status': motion_data})

# Flask route to handle manual control of the buzzer
@app.route('/control', methods=['POST'])
def control():
    global manual_buzzer_control
    action = request.form.get('action')
    if action == 'start':
        manual_buzzer_control = True
        buzzer.on()  # Turn on the buzzer manually
    elif action == 'stop':
        manual_buzzer_control = False
        buzzer.off()  # Turn off the buzzer manually
    return redirect(url_for('index'))  # Redirect to home page after action

# Function to continuously update motion detection status in a separate thread
if __name__ == '__main__':
    threading.Thread(target=update_motion_data, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
