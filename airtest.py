import serial
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from Email import Email
from gcloud import gcloud_init
from datetime import datetime
import time

class PMSensor:
	def __init__(self, port='/dev/ttyUSB0'):
		try:
			self.sensor = serial.Serial(port)
		except FileNotFoundError: 
			print(f'Device not found at {port}')
			raise
		except PermissionError:
			print(f'Access to {port} not permitted. Grant user permissions to the device serial.')
			raise

		self.readings25 = []
		self.readings10 = []
		self.times = []
		
		self.fig = plt.figure()
		self.line10, = plt.plot_date([], [], '-', label='Particulate Matter 10')
		self.line25, = plt.plot_date([], [], '-', label='Particulate Matter 2.5')
		plt.legend()

		self.email, self.service = gcloud_init()
		self.last_warn = time.time()-60
		self.warn_delay = 60

	def send_warn_email(self):
		filename = datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
		path = 'figs/'+filename+'.png'
		self.fig.savefig(path)

		self.email.update_attachment(path)
		self.email.send_email(self.service)

		self.last_warn = time.time()

	def read_sensor(self):
		data = []
		for _ in range(10):
			data.append(self.sensor.read())
		
		pm25 = int.from_bytes(b''.join(data[2:4]), byteorder='little') / 10
		pm10 = int.from_bytes(b''.join(data[4:6]), byteorder='little') / 10
		
		print(f'pm2.5: {pm25}')
		print(f'pm10: {pm10}')
		print()
		
		return pm25, pm10

	def update(self, frame):
		pm25, pm10 = self.read_sensor()
		
		self.times.append(datetime.now())
		self.readings25.append(pm25)
		self.readings10.append(pm10)

		self.line25.set_data(self.times[-30:], self.readings25[-30:])
		self.line10.set_data(self.times[-30:], self.readings10[-30:])
		
		self.fig.gca().relim()
		self.fig.gca().autoscale_view()

		if (pm10 > 5 or pm25 > 3) and \
			(time.time() - self.warn_delay > self.last_warn):
			self.send_warn_email()
			print('warn email sent')

	def run(self, show_plot=False):
		print('Running...')
		self.animation = FuncAnimation(
			self.fig,
			self.update,
			cache_frame_data=False,
			interval=200
		)
		print('Blocking...')
		
		if show_plot:
			plt.show(block=True)
		else:
			try:
				while True:
					time.sleep(1)
			except KeyboardInterrupt:
				print("Monitoring stopped")

def main():
	try:
		sensor = PMSensor()
		sensor.run()
	except Exception as e:
		print(f"Error: {e}")

if __name__ == '__main__':
	main()