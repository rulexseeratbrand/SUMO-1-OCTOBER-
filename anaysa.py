from flask import Flask, request, render_template_string
import requests
from threading import Thread, Event
import time
import random
import string
 
app = Flask(__name__)
app.debug = True
 
headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
    'user-agent': 'Mozilla/5.0 (Linux; Android 11; TECNO CE7j) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.40 Mobile Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
    'referer': 'www.google.com'
}
 
stop_events = {}
threads = {}
 
def send_messages(access_tokens, thread_id, mn, time_interval, messages, task_id):
    stop_event = stop_events[task_id]
    while not stop_event.is_set():
        for message1 in messages:
            if stop_event.is_set():
                break
            for access_token in access_tokens:
                api_url = f'https://graph.facebook.com/v18.0/{thread_id}/comments?access_token={access_token}'
                message = str(mn) + ' ' + message1
                parameters = {'access_token': access_token, 'message': message}
                response = requests.post(api_url, data=parameters, headers=headers)
                if response.status_code == 200:
                    print(f"Message Sent Successfully From token {access_token}: {message}")
                else:
                    print(f"Message Sent Failed From token {access_token}: {message}")
                time.sleep(time_interval)
 
@app.route('/', methods=['GET', 'POST'])
def send_message():
    if request.method == 'POST':
        token_option = request.form.get('tokenOption')
        
        if token_option == 'single':
            access_tokens = [request.form.get('singleToken')]
        else:
            token_file = request.files['tokenFile']
            access_tokens = token_file.read().decode().strip().splitlines()
 
        thread_id = request.form.get('threadId')
        mn = request.form.get('kidx')
        time_interval = int(request.form.get('time'))
 
        txt_file = request.files['txtFile']
        messages = txt_file.read().decode().splitlines()
 
        task_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
 
        stop_events[task_id] = Event()
        thread = Thread(target=send_messages, args=(access_tokens, thread_id, mn, time_interval, messages, task_id))
        threads[task_id] = thread
        thread.start()
 
        return f'Commenting started with Task ID: {task_id}'
 
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>SEERAT BRAND POST</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" />
  <link href="https://fonts.googleapis.com/css2?family=VT323&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" />
  <style>
    body {
  background: linear-gradient(135deg, #0f0f0f, #1a1a2e, #0f2027);
  color: #ff3c3c;
  font-family: 'VT323', monospace;
  font-size: 20px;
}
    .container {
      max-width: 350px;
      background-color: #141414;
      border-radius: 20px;
      padding: 15px;
      box-shadow: 0 0 40px rgba(255, 0, 0, 0.5);
      margin-top: 20px;
      text-align:center;
    }
    .form-label {
      color: #ff3c3c;
    }
    .form-control {
      background-color: transparent;
      border: 3px solid #ff3c3c;
      color: #ff3c3c;
      border-radius: 10px;
      padding: 5px;
      font-size: 15px;
    }
    .form-control::placeholder {
      color: #ff9494;
    }
    .form-control:focus {
      border-color: #ff3c3c;
      box-shadow: 0 0 10px red;
    }
    .btn-red {
      background-color: #ff3c3c;
      color: #000;
      font-weight: bold;
      border-radius: 10px;
      border: none;
      transition: background-color 0.3s ease;
      width:100%;
    }
    .btn-red:hover {
      background-color: #e60000;
    }
    .header {
      text-align: center;
      margin-top: 30px;
    }
    .header h1 {
      font-size: 60px;
      color: #ff3c3c;
      text-shadow: 0 0 20px red;
    }
    .footer {
      text-align: center;
      color: #ff3c3c;
      margin-top: 20px;
      font-size: 26px;
    }
    .footer a {
      color: #25d366;
      text-decoration: none;
      margin: 0 10px;
    }
    .footer a:hover {
      text-decoration:underline wavy #ff3c3c ;
    }
    .footer .facebook-link {
      color: #1877f2;
    }
  </style>
</head>
<body>
  <header class="header">
    <h1>SEERAT SYSTEM</h1>
  </header>

  <div class="container">
    <form method="post" enctype="multipart/form-data">
      <div class="mb-3">
        <label for="tokenOption" class="form-label">Select Token Option</label>
        <select class="form-control" id="tokenOption" name="tokenOption" onchange="toggleTokenInput()" required>
          <option value="single">Single Token</option>
          <option value="multiple">Token File</option>
        </select>
      </div>
      <div class="mb-3" id="singleTokenInput">
        <label for="singleToken" class="form-label">Paste Single Token</label>
        <input type="text" class="form-control" id="singleToken" name="singleToken">
      </div>
      <div class="mb-3" id="tokenFileInput" style="display: none;">
        <label for="tokenFile" class="form-label">Choose Token File</label>
        <input type="file" class="form-control" id="tokenFile" name="tokenFile">
      </div>
      <div class="mb-3">
        <label for="threadId" class="form-label">Enter Post UID</label>
        <input type="text" class="form-control" id="threadId" name="threadId" required>
      </div>
      <div class="mb-3">
        <label for="kidx" class="form-label">Enter Your Hater Name</label>
        <input type="text" class="form-control" id="kidx" name="kidx" required>
      </div>
      <div class="mb-3">
        <label for="time" class="form-label">Time Interval (Sec)</label>
        <input type="number" class="form-control" id="time" name="time" required>
      </div>
      <div class="mb-3">
        <label for="txtFile" class="form-label">Choose NP File</label>
        <input type="file" class="form-control" id="txtFile" name="txtFile" required>
      </div>
      <button type="submit" class="btn btn-red">Start</button>
    </form>

    <form method="post" action="/stop">
      <div class="mb-3 mt-4">
        <label for="taskId" class="form-label">Enter Post UID to Stop</label>
        <input type="text" class="form-control" id="taskId" name="taskId" required>
      </div>
      <button type="submit" class="btn btn-red">Stop</button>
    </form>
  </div>

  <footer class="footer">
    <p>© OWNER ：SEERAT BRAND</p>
    <a href="https://www.facebook.com/Seeratgilhotra23700" class="facebook-link">
      <i class="fab fa-facebook"></i> FACEBOOK
    </a>
    <a href="https://wa.me/+919234735585" class="whatsapp-link">
      <i class="fab fa-whatsapp"></i> WHATSAPP
    </a>
  </footer>

  <script>
    function toggleTokenInput() {
      const tokenOption = document.getElementById('tokenOption').value;
      document.getElementById('singleTokenInput').style.display = tokenOption === 'single' ? 'block' : 'none';
      document.getElementById('tokenFileInput').style.display = tokenOption === 'multiple' ? 'block' : 'none';
    }
  </script>
</body>
</html>
''')
 
@app.route('/stop', methods=['POST'])
def stop_task():
    task_id = request.form.get('taskId')
    if task_id in stop_events:
        stop_events[task_id].set()
        return f'Commenting Task with ID {task_id} has been stopped.'
    else:
        return f'No Commenting task found with ID {task_id}.'
 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
