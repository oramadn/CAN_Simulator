from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QGridLayout
from PySide6.QtCore import QTimer
import pyqtgraph as pg
import threading
import time


class RealTimePlotter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-Time Data Plotter")
        self.resize(800, 600)
        self.running = True  # Control flag for the thread loop
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QGridLayout(central_widget)

        self.graphs = {}
        self.data = {'throttle': [], 'brake': [], 'steer_right': [], 'steer_left': []}
        self.time_data = []
        colors = {'throttle': 'r', 'brake': 'b', 'steer_right': 'g', 'steer_left': 'y'}
        titles = {'throttle': "Throttle (0-180)", 'brake': "Brake (0-100)", 'steer_right': "Steer Right (0-360)",
                  'steer_left': "Steer Left (0-360)"}

        font = {'color': 'w', 'font-size': '10pt'}

        for i, (key, color) in enumerate(colors.items()):
            plot_widget = pg.PlotWidget()
            plot_widget.setBackground('w')  # Ensure background is set to dark mode

            # Customize the plot to have a dark theme
            plot_widget.setTitle(titles[key], color='k')
            plot_widget.showGrid(x=True, y=True, alpha=0.3)

            for axis in ['left', 'bottom']:
                plot_widget.getPlotItem().getAxis(axis).setPen(pg.mkPen('k'))
                plot_widget.getPlotItem().getAxis(axis).setTextPen(pg.mkPen('k'))
                label = key.capitalize() if axis == 'left' else 'Time (s)'
                plot_widget.getPlotItem().getAxis(axis).setLabel(text=label, units='', **font)

            self.graphs[key] = plot_widget.plot(pen=color)
            layout.addWidget(plot_widget, i // 2, i % 2)

        self.timer = QTimer(self)
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_plots)
        self.timer.start()

    def closeEvent(self, event):
        self.running = False  # Signal threads to stop
        self.timer.stop()  # Stop the timer
        super().closeEvent(event)  # Proceed with closing the window

    def update_plots(self):
        if not self.running:
            return
        for key, graph in self.graphs.items():
            if len(self.data[key]) > 0:
                graph.setData(self.time_data, self.data[key])

    def fetch_data(self, fetch_function, key):
        while self.running:  # Check if still running
            value = fetch_function()
            scaled_value = self.scale_data(value, key)
            self.data[key].append(scaled_value)
            if len(self.time_data) < len(self.data[key]):
                self.time_data.append(len(self.time_data))
            time.sleep(1)  # Adjust this sleep as necessary

    def start_data_threads(self, data_fetch_functions):
        for key, func in data_fetch_functions.items():
            thread = threading.Thread(target=self.fetch_data, args=(func, key))
            thread.start()

    def scale_data(self, value, key):
        if key == 'throttle':
            return value * 180 / 255
        elif key == 'brake':
            return value * 100 / 255
        elif key in ['steer_right', 'steer_left']:
            return value * 360 / 255
        return value
