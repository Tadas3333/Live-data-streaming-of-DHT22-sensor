import Adafruit_DHT
import http.server, socketserver

PIN = 4
PORT = 80

page_html = """
<!DOCTYPE html>
<html>
	<head>
		<title>Sensor</title>
		<style>
			#loader {
				margin-left: 10px;
				border: 5px solid #f3f3f3;
				border-top: 5px solid #555555;
				border-radius: 50%;
				width: 10px;
				height: 10px;
				animation: spin 2s linear infinite;
				float: left;
			}

			@keyframes spin {
				0% { transform: rotate(0deg); }
				100% { transform: rotate(360deg); }
			}

			#sensoriaus-info {
				width: 350px;
				height: 23px;
				font-size: 18px;
				padding: 15px;
				color: #ffffff;
				background-color: #008822;
			}

			#sensoriaus-text {
				float: left;
			}

		</style>
	</head>

	<body>
		<div id='sensoriaus-info'>
            <div id='sensoriaus-text'>Loading...</div>
            <div id='loader'></div>
        </div>

		<script>
			const Http = new XMLHttpRequest();
			Http.addEventListener('error', errorHandler);
			var requestSent = false;

			function errorHandler(e) {
				reportError();
                console.log("errorHandler: " + e.message);
			}
            
            function reportError() {
 				document.getElementById('sensoriaus-text').textContent = "Error!";
				document.getElementById('sensoriaus-info').style.backgroundColor = '#aa2222';           
            }

			function sendRequest(){
				if(requestSent == false) {
					requestSent = true;
					try {
						Http.open('GET','data', true);
						Http.send();
					}catch(e) {
						reportError();
						console.log(e.message);
						return;
					}
				}
				setTimeout(sendRequest, 1000);
			}

			Http.onreadystatechange = (e) => {
				if(Http.readyState == 4 && Http.status == 200) {
					document.getElementById('sensoriaus-text').textContent = Http.responseText;
					requestSent = false;
				}
				else if(Http.status != 200 && Http.status != 0){
					reportError();
					console.log('Http status: ' + Http.status);
					console.log('Http readyState: ' + Http.readyState);
				}
			}

			sendRequest();
		</script>
	</body>
</html>
"""

def getSensorInfo():
	humidity, temperature = Adafruit_DHT.read(Adafruit_DHT.DHT22,PIN)
	if humidity is not None and temperature is not None:
		return "Temperature {0:0.1f}*c, Humidity {1:0.1f}%".format(temperature, humidity)
	else:
		return "Temperature _*c, Humidity _%"

class PageHandler(http.server.SimpleHTTPRequestHandler):
	def do_GET(s):
		data = ""

		if s.path == "/data":
			data = getSensorInfo()
		else:
			data = page_html

		data = data.encode()

		s.send_response(200)
		s.send_header("Content-type", "text/html")
		s.send_header("Content-length", str(len(data)))
		s.end_headers()

		s.wfile.write(data)

server = http.server.HTTPServer(('',PORT), PageHandler)
server.serve_forever()
 
