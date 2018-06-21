<img src="assets/hero.png" ><br><br>
<a href="mailto:dev.dibyo@gmail.com">&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp; ![Ask Me Anything](https://img.shields.io/badge/Ask%20me-anything-1abc9c.svg?longCache=true&style=plastic)</a> [![made-with-python](https://img.shields.io/badge/Made%20with-Python-blue.svg?longCache=true&style=plastic)](https://www.python.org/) [![GitHub license](https://img.shields.io/github/license/Naereen/StrapDown.js.svg?longCache=true&style=plastic)](https://github.com/Naereen/StrapDown.js/blob/master/LICENSE) ![PyPI - Status](https://img.shields.io/pypi/status/Django.svg?style=plastic)<br><br>

Automatic Parking System is a parking solution designed for the modern establishments that want to manage their parking lot without human assistance. The proposed system consists of fully automated toll gates that control the entry and exit of the vechicles into and from the parking lot. It also features the ability to restrict the entry of blacklisted cars. The live status of the parking slots can be viewed through a mobile application designed for the system admins. The number plates of the cars are recorded on their entry/exit using OCR. The timing of their entry/exit, number plates and the number of empty slots are recorded and stored in database on every operation of the toll gates.
<br><br>

#### Dependencies

- Python 3.
- Google Cloud Platform - Vision API.
- OpenCV.
- Raspberry Pi 3.
- PiCamera.
- MG995 servo motors x2.
- IR modules x2.
- Thingspeak.
- Companion App.
<br><br>

#### Usage

- Connect the sensors to Raspberry Pi as follows.

&emsp;&emsp;1. <code>IR sensor 1</code> to <code>GPIO 16</code>.<br>
&emsp;&emsp;2. <code>IR sensor 2</code> to <code>GPIO 18</code>.<br>
&emsp;&emsp;3. Connect the PCA9865 driver via I2C connection.<br>
&emsp;&emsp;4. <code>Motor 1</code> to <code>Pin 0</code> of PCA9685.<br>
&emsp;&emsp;5. <code>Motor 2</code> to <code>Pin 15</code> of PCA9685.<br>
&emsp;&emsp;5. Connect the PiCamera.
<br>
<br>

- Replace the following line in <code>run.py</code> with the Vision API credentials.

&emsp;&emsp;<code>os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'GCP_SERVICE_ACCOUNT_CREDENTIALS.json'</code>
<br><br>

- Create a Thingspeak Account and create a new project with the following fields.<br>
<code>number_plate , slots_remaining , status </code>
<br><br>
- Create new project in MIT App inventor and create the following blocks.

<table>
	<tr>
		<td>
			<a href="assets/mit_design_1.JPG"><img src="assets/mit_design_1.JPG"></a>
			&emsp;&emsp;&emsp;&emsp;&emsp;Design View of Screen 1
		</td>
		<td>
			<a href="assets/mit_block_1.png"><img src="assets/mit_block_1.png"></a>
			<br><br>&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;Block View of Screen 1
		</td>
	</tr>
	<tr>
		<td>
			<a href="assets/mit_design_2.JPG"><img src="assets/mit_design_2.JPG"></a>
			<br><br>&emsp;&emsp;&emsp;&emsp;&emsp;Design View of Screen 2
		</td>
		<td>
			<a href="assets/mit_block_2.png"><img src="assets/mit_block_2.png"></a>
			&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;Block View of Screen 2
		</td>
	</tr>
</table>
<br><br>
- Run the script on Raspberry Pi as follows <br>
<code>python3 run.py</code>
<br><br>

#### Demonstration

- The follwoing image shows the OCR operation 
<br><br>
<a href="assets/ocr.JPG">&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;<img src="assets/ocr.JPG" width="700px"></a>
<br><br>
- The following images show the live monitoring from the companion app.
<br><br>
<table>
	<tr>
		<td>
			<a href="assets/1.jpeg"><img src="assets/1.jpeg"></a>
			<h6>1. Installation.</h6>
		</td>
		<td>
			<a href="assets/2.jpeg"><img src="assets/2.jpeg"></a>
			<h6>2. Home Page.</h6>
		</td>
		<td>
			<a href="assets/3.jpeg"><img src="assets/3.jpeg"></a>
			<h6>3. After Login.</h6>
		</td>
	</tr>
	<tr>
		<td>
			<a href="assets/4.jpeg"><img src="assets/4.jpeg"></a>
			<h6>4. Current parking slots available.</h6>
		</td>
		<td>
			<a href="assets/5.jpeg"><img src="assets/5.jpeg"></a>
			<h6>5. Downloading database.</h6>
		</td>
		<td>
			<a href="assets/6.jpeg"><img src="assets/6.jpeg"></a>
			<h6>6. Database in .xls format.</h6>
		</td>
	</tr>
</table>
<br><br>
© All rights reserved.