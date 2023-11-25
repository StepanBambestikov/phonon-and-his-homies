from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QBrush, QColor
from widgets import Ui_MainWindow
import controller
import numpy as np
from pyqtgraph import PlotWidget
import pyqtgraph as pg

class ManagerException(Exception):
    """
    Special Exception type for view error_manager, generated only by error manager and catches in main button function
    (view_window.collect_information_with_error_check)
    """
    pass


def exec_function_with_error_check(function):
    """used for catching our errors and continuation of the program"""
    try:
        function()
    except ManagerException:
        return


class view_window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.k_coef = 100
        self.graph_length = 100
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        big_small_pixel_diff = 120
        self.controller = controller.controller(big_small_pixel_diff)
        self._connectSignalsSlots()
        self.error_message = QMessageBox()
        self.error_message.setIcon(QMessageBox.Critical)
        self.main_y = 10
        # self.circle = pg.CircleROI(10, self.main_y, size=10, brush='r')
        self.circle = pg.CircleROI([250, 250], [120, 120], pen=pg.mkPen('r',width=2))
        self.ui.graphView.addItem(self.circle)

        self.ui.AcosticRadioButton.clicked.connect(self.call_acoustic)
        self.ui.OpticalRadioButton.clicked.connect(self.call_optical)

        self.timer = QTimer()
        self.timer.timeout.connect(self.main_loop_iteration)
        self.timer.start(1)

        self.a = 1
        self.atom_scene = QGraphicsScene(self.ui.centralwidget)
        self.ui.AtomsView.setScene(self.atom_scene)
        self.ui.WaveSlider.setRange(int(-(self.k_coef * np.pi) / (self.a * 2)), int((self.k_coef * np.pi) / (self.a * 2)))
        self.ui.TimeSlider.setRange(1, 10)
        begin_big_x0 = -500
        begin_small_x0 = begin_big_x0 + (big_small_pixel_diff / 2)
        self.big_atoms_x0 = np.array([[begin_big_x0 + i * big_small_pixel_diff, 10] for i in range(4)])
        self.small_atoms_x0 = np.array([[begin_small_x0 + i * big_small_pixel_diff, 10] for i in range(4)])
        self.update_parameters()

    def main_loop_iteration(self):
        self.atom_scene.clear()
        self.controller.set_k((self.ui.WaveSlider.value() / self.controller.distance) / 100)
        big_atoms_diff, small_atoms_diff, current_graph_circle_x = self.controller.get_atoms(self.ui.TimeSlider.value() / 1000)
        # TODO current_graph_circle_x for plotting circle in graphView!
        # self.circle.setPos(current_graph_circle_x * self.graph_length * (self.ui.WaveSlider.value() / 100), self.main_y)

        for current_index in range(self.big_atoms_x0.shape[0]):
            circle = self.atom_scene.addEllipse(self.big_atoms_x0[current_index, 0] - 25 + big_atoms_diff, self.big_atoms_x0[current_index, 1] - 25, 50, 50, Qt.black)
            circle.setBrush(QBrush(QColor(255, 0, 0)))

        for current_index in range(self.big_atoms_x0.shape[0]):
            circle = self.atom_scene.addEllipse(self.small_atoms_x0[current_index, 0] - 10 + small_atoms_diff, self.small_atoms_x0[current_index, 1] - 10, 20,
                                                20, Qt.black)
            circle.setBrush(QBrush(QColor(255, 0, 0)))

    def _show_error_message(self, informative_text):
        self.error_message.setInformativeText(informative_text)
        self.error_message.setWindowTitle("Error!")
        self.error_message.exec_()
        raise ManagerException

    def update_parameters(self):
        """reading all parameters when you press the start button and sending them to the controller"""
        M = self.get_valid_float_parameter_from_line_edit(self.ui.FirstMassLineEdit, "Invalid M parameter!")
        m = self.get_valid_float_parameter_from_line_edit(self.ui.SecondMassLineEdit, "Invalid m parameter!")
        distance = self.get_valid_float_parameter_from_line_edit(self.ui.DistanceLineEdit,
                                                                 "Invalid distance parameter!")
        C = self.get_valid_float_parameter_from_line_edit(self.ui.KLineEdit, "Invalid C parameter!")
        self.controller.update_parameters(M, m, distance, C)
        self.ui.graphView.clear()
        x, optical_y, acoustic_y = self.controller.get_graph()
        self.ui.graphView.plot(x, optical_y)
        self.ui.graphView.plot(x, acoustic_y)

    def get_valid_float_parameter_from_line_edit(self, line_edit, error_message):
        try:
            valid_parameter = float(line_edit.text())
        except Exception:
            self._show_error_message(error_message)
        return valid_parameter

    def _connectSignalsSlots(self):
        self.ui.startButton.clicked.connect(lambda: exec_function_with_error_check(self.update_parameters))

    def call_acoustic(self):
        self.controller.set_acoustic()

    def call_optical(self):
        self.controller.set_optic()
