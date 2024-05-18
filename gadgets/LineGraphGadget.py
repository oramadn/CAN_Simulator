import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PySide6.QtCore import Qt, QTimer, QRandomGenerator
from PySide6.QtGui import QPainter, QColor, QBrush


class LineChartWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.series = QLineSeries()  # Line series to hold data
        self.series.setColor(QColor(0, 119, 190))  # Set the line color

        self.setAttribute(Qt.WA_TranslucentBackground)  # Enable transparency
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.chart = QChart()
        self.chart.addSeries(self.series)
        self.chart.legend().hide()
        # self.chart.setTitle("Dynamic Line Chart")
        self.chart.setBackgroundBrush(QBrush(QColor(30, 30, 30)))  # Dark background
        self.chart.setTitleBrush(QBrush(Qt.white))  # White text for title

        # Numeric axis for X (Time in seconds)
        self.axisX = QValueAxis()
        self.axisX.setRange(0, 4)  # Initially set to show up to 4 seconds
        self.axisX.setLabelFormat("%.1f s")
        self.axisX.setTitleText("Time (seconds)")
        self.axisX.setTitleBrush(QBrush(Qt.white))  # White text for axis title
        self.axisX.setLabelsColor(Qt.white)  # White text for labels
        self.axisX.setGridLineVisible(True)
        self.axisX.setMinorTickCount(4)  # Smaller grid divisions
        self.axisX.setMinorGridLineVisible(True)
        self.axisX.setMinorGridLineColor(QColor(50, 50, 50))  # Darker minor grid lines for subtle appearance
        self.chart.addAxis(self.axisX, Qt.AlignBottom)
        self.series.attachAxis(self.axisX)

        # Value axis for Y
        self.axisY = QValueAxis()
        self.axisY.setLabelFormat("%i")
        self.axisY.setTitleText("Value")
        self.axisY.setTitleBrush(QBrush(Qt.white))  # White text for axis title
        self.axisY.setLabelsColor(Qt.white)  # White text for labels
        self.axisY.setRange(0, 265)
        self.axisY.setGridLineVisible(True)
        self.axisY.setMinorTickCount(4)  # More frequent minor ticks
        self.axisY.setMinorGridLineVisible(True)
        self.axisY.setMinorGridLineColor(QColor(50, 50, 50))  # Subtle minor grid lines
        self.chart.addAxis(self.axisY, Qt.AlignLeft)
        self.series.attachAxis(self.axisY)

        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setContentsMargins(0, 0, 0, 0)  # Reduce padding within the chart view
        self.setCentralWidget(self.chart_view)

        self.time_elapsed = 0.0  # Track elapsed time in seconds

    def set_value(self, value):
        self.series.append(self.time_elapsed, value)
        # Extend the x-axis range if necessary
        if self.time_elapsed >= self.axisX.max() - 1:
            self.axisX.setMax(self.axisX.max() + 1)
        self.time_elapsed += 0.05  # Increment time by 0.05 seconds


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LineChartWidget()
    window.resize(800, 600)
    window.show()

    # Simulate incoming data
    timer = QTimer()
    timer.timeout.connect(lambda: window.set_value(QRandomGenerator.global_().bounded(255)))
    timer.start(100)  # Update interval set to 100 ms for smoother updates

    sys.exit(app.exec())
