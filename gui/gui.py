import math
import sympy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter, QPen, QImage
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QFrame, QLabel, QPushButton
from PyQt5 import QtCore, QtGui, QtWidgets
from sympy import latex

from graph_functions.polynomial_getter import PolynomialGetter
from graph_functions.supporting import *


class OkButton(QPushButton):
    def __init__(self, dialog, widget):
        super().__init__(widget)
        self.setup_ui()
        self.dialog = dialog
        self.widget = widget
        self.settings = None

    def set_settings(self, settings):
        self.settings = settings

    def setup_ui(self):
        self.setGeometry(QtCore.QRect(100, 160, 101, 31))
        self.setObjectName("pushButton")

    def mousePressEvent(self, e):
        if check_int(self.dialog.lineEdit.text()):
            if self.dialog.type:
                self.settings.current_weight = int(self.dialog.lineEdit.text())
                self.widget.hide()
            else:
                self.settings.start_vertex = int(self.dialog.lineEdit.text())
                self.widget.hide()
                self.show_polynomials()

    def show_polynomials(self):
        getter = PolynomialGetter(self.settings.edges, self.settings.start_vertex, self.settings.weights.copy())
        getter.get()
        getter.write_file()
        getter.set_ones()
        getter.get()
        svg = QSvgWidget()
        svg.load(tex2svg(to_raw(latex(getter.polynomial_result))))
        svg.setWindowTitle("Output")
        svg.show()


class UiDialog(object):
    def __init__(self, settings):
        self.lineEdit = None
        self.pushButton = None
        self.label = None
        self.type = None
        self.settings = settings

    def setup_ui(self, Dialog):
        Dialog.setObjectName("Ввод")
        Dialog.resize(300, 200)
        Dialog.setMinimumSize(QtCore.QSize(300, 200))
        Dialog.setMaximumSize(QtCore.QSize(300, 200))
        self.lineEdit = QtWidgets.QLineEdit(Dialog)
        self.lineEdit.setGeometry(QtCore.QRect(50, 100, 200, 25))
        self.lineEdit.setObjectName("lineEdit")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(25, 40, 250, 41))
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setObjectName("label")
        self.pushButton = OkButton(self, Dialog)
        self.pushButton.set_settings(self.settings)

        self._retranslate_ui(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def set_type(self, type_of_dialog):
        self.type = type_of_dialog

    def _retranslate_ui(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Ввод"))
        if self.type:
            self.label.setText(_translate("Dialog", "Введите квадрат веса ребра"))
        else:
            self.label.setText(_translate("Dialog", "Введите номер стартовой вершины"))

        self.pushButton.setText(_translate("Dialog", "OK"))


class VertexLabel(QLabel):
    def __init__(self, widget, num):
        super().__init__(widget)
        self.setGeometry(QtCore.QRect(45, 10, 50, 50))
        self.setObjectName("label")
        self.setText(str(num))
        myFont = QtGui.QFont()
        myFont.setBold(True)
        self.setFont(myFont)
        self.show()


class EdgeWeightLabel(QLabel):
    def __init__(self, widget, first, second):
        super().__init__(widget)
        self.setGeometry(QtCore.QRect((first.pos.x() + second.pos.x()) // 2,
                                      (first.pos.y() + second.pos.y()) // 2,
                                      30,
                                      30))
        self.setObjectName("label")
        myFont = QtGui.QFont()
        myFont.setBold(True)
        self.setFont(myFont)
        self.show()


class Vertex(QLabel):
    def __init__(self, frame, visitor):
        super().__init__(frame)
        self.setGeometry(QtCore.QRect(0, 0, 50, 50))
        self.setObjectName("label")
        self.setPixmap(QPixmap("vertex.png").scaled(100, 100))
        self.setStyleSheet("background-color: transparent;")
        self.visitor = visitor
        self.show()
        self.frame = frame
        self.number = 0
        self.text = None
        self.pos = None
        self.set_text_label()

    def set_location(self, x, y):
        self.setGeometry(QtCore.QRect(x - 49, y - 35, 80, 70))

    def mousePressEvent(self, event):
        self.visitor.add_to_pressed(self)

    def set_text_label(self):
        self.number = self.visitor.get_number()
        self.text = VertexLabel(self, self.number)


class ClearButton(QPushButton):
    def __init__(self, widget):
        super().__init__(widget)
        self.settings = None

    def set_visitor(self, settings):
        self.settings = settings

    def mousePressEvent(self, e):
        self.settings.clear()


class BuildButton(QPushButton):
    def __init__(self, widget):
        super().__init__(widget)
        self.settings = None

    def set_settings(self, settings):
        self.settings = settings

    def mousePressEvent(self, e):
        dialog = QtWidgets.QDialog()
        ui_dialog = UiDialog(self.settings)
        ui_dialog.set_type(False)
        ui_dialog.setup_ui(dialog)
        dialog.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)
        dialog.exec_()


class Settings:
    def __init__(self, frame):
        self._qp = None
        self.frame = frame
        self.vertexes = []
        self.pressed = []
        self.edge_weights = []
        self.number = 0
        self.edges = []
        self.current_weight = 0
        self.start_vertex = 0
        self.weights = []
        self.init_weights()

    def init_weights(self):
        for i in range(20):
            temp = [0] * 20
            self.weights.append(temp)

    def set_painter(self, qp):
        self._qp = qp

    def add_to_pressed(self, vertex):
        for i in range(len(self.pressed)):
            if self.pressed[i] == vertex:
                self.pressed.pop(i)
                return
        self.pressed.append(vertex)
        if len(self.pressed) == 2:
            self.connect()

    def connect(self):
        painter = QPainter(self.frame.image)
        painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
        painter.drawLine(self.pressed[0].pos, self.pressed[1].pos)
        edge_label = EdgeWeightLabel(self.frame, *self.pressed)
        self.edges[self.pressed[0].number].append(self.pressed[1].number)
        self.edges[self.pressed[1].number].append(self.pressed[0].number)
        self.create_window()
        self.edge_weights.append(edge_label)
        self.frame.update()
        if self._is_square_root():
            edge_label.setText(str(int(math.sqrt(self.current_weight))))
        else:
            edge_label.setText("√" + str(self.current_weight))

        self.weights[self.pressed[0].number][self.pressed[1].number] = sympy.sqrt(self.current_weight)
        self.weights[self.pressed[1].number][self.pressed[0].number] = sympy.sqrt(self.current_weight)
        self.pressed.clear()

    def _is_square_root(self):
        current = int(math.sqrt(self.current_weight))
        return (current ** 2) == (math.sqrt(self.current_weight) ** 2)

    def create_window(self):
        dialog = QtWidgets.QDialog()
        ui_dialog = UiDialog(self)
        ui_dialog.set_type(True)
        ui_dialog.setup_ui(dialog)
        dialog.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)
        dialog.exec_()

    def clear(self):
        for vertex in self.vertexes:
            vertex.hide()
        for edge in self.edge_weights:
            edge.hide()
        self.vertexes = []
        self.pressed = []
        self.edges = []
        self.edge_weights = []
        self.number = 0
        self.weights = []
        self.init_weights()
        self.frame.clear()

    def get_number(self):
        self.number += 1
        return self.number - 1


class PaintingFrame(QFrame):
    def __init__(self, widget):
        super().__init__(widget)
        self._widget = widget
        self.settings = Settings(self)
        self.setObjectName("frame")
        self.image = QImage(widget.size(), QImage.Format_RGB32)
        self.image.fill(Qt.white)

    def paintEvent(self, e):
        canvas_painter = QPainter(self)
        canvas_painter.drawImage(self.rect(), self.image, self.image.rect())

    def mousePressEvent(self, event):
        label = Vertex(self, self.settings)
        label.set_location(event.x(), event.y())
        label.pos = event.pos()
        print(label.pos)
        self.settings.vertexes.append(label)
        self.settings.edges.append([])

    def clear(self):
        self.image.fill(Qt.white)
        self.update()


class UiMainWindow(object):
    def setup_ui(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        MainWindow.setFixedSize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.pushButton = ClearButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(635, 225, 161, 41))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = BuildButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(635, 275, 161, 41))
        self.pushButton_2.setObjectName("pushButton_2")
        self.verticalFrame = QtWidgets.QFrame(self.centralwidget)
        self.verticalFrame.setGeometry(QtCore.QRect(10, 10, 631, 531))
        self.verticalFrame.setMouseTracking(False)
        self.verticalFrame.setObjectName("verticalFrame")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalFrame)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = PaintingFrame(self.verticalFrame)
        self.pushButton.set_visitor(self.frame.settings)
        self.pushButton_2.set_settings(self.frame.settings)
        self.verticalLayout.addWidget(self.frame)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self._retranslate_ui(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def _retranslate_ui(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Программа для построения многочлена"))
        self.pushButton.setText(_translate("MainWindow", "Очистить поле"))
        self.pushButton_2.setText(_translate("MainWindow", "Построить многочлен"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = UiMainWindow()
    ui.setup_ui(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
