import os
import subprocess
import sys
from PyQt6.QtCore import Qt, QRectF, QPoint, QRectF, QPointF
from PyQt6.QtGui import QPainter, QPen, QColor, QPainterPath, QMouseEvent, QPaintEvent
import PyQt6.QtWidgets as wgs
from scripts.buttons import Buttons, ProgramState
from pygifsicle import gifsicle


try:
    from ctypes import windll
    myappid = 'gifcapture.gifcapture.capture.1'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass


class MainWindow(wgs.QWidget):

    def __init__(self):
        super().__init__()
        # Get desktop size
        self.desktop_height = wgs.QApplication.primaryScreen().geometry().height()
        self.desktop_width = wgs.QApplication.primaryScreen().geometry().width()

        self.setMinimumSize(self.desktop_width, self.desktop_height)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)  # |
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.locked = False
        # Selection Area
        self.start_pos = QPoint()
        self.end_pos = QPoint()
        self.is_selected = False

        # Corners
        self.selection_corners = [
            # Corners
            CornerItem(0, 0),
            CornerItem(1, 1),
            CornerItem(0, 2),
            CornerItem(1, 3),

            # Edges
            CornerItem(2, 4),
            CornerItem(3, 5),
            CornerItem(2, 6),
            CornerItem(3, 7),
        ]
        self.clicked_corner = None

        # Selection Tranform Scene
        selection_scene = wgs.QGraphicsScene()

        selection_scene.setSceneRect(
            0, 0, self.desktop_width, self.desktop_height)

        # Add Selection to scene
        pen = QPen(Qt.GlobalColor.white, 4, Qt.PenStyle.DashLine)
        pen.setDashPattern([4, 4])
        self.selected_area = selection_scene.addRect(QRectF(), pen)

        # Add Corners to scene
        for corner in self.selection_corners:
            selection_scene.addItem(corner)

        # Init Scene after everything is added
        self.selection_scene = selection_scene

        # Selection Tranform View
        selection_view = View(self.selection_scene, self)
        self.selection_view = selection_view

        # Buttons Scene
        buttons_scene = wgs.QGraphicsScene()

        # Init Scene after everything is added
        self.buttons_scene = buttons_scene

        # Buttons View
        buttons_view = Buttons(self.buttons_scene, self)
        buttons_view.setParent(selection_view)
        self.buttons_view = buttons_view

        # Layout
        layout = wgs.QVBoxLayout()
        layout.addWidget(selection_view)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def lockTransform(self, locked):
        self.setCornerVisibility(not locked)
        self.selected_area.setVisible(not locked)
        self.locked = locked
        self.update()

    def updateCornerPositions(self):
        self.setCornerVisibility(True)
        rect = self.selected_area.rect()
        tl = rect.topLeft()
        tr = rect.topRight()
        br = rect.bottomRight()
        bl = rect.bottomLeft()
        t = (rect.topLeft() + rect.topRight()) / 2
        r = (rect.topRight() + rect.bottomRight()) / 2
        b = (rect.bottomLeft() + rect.bottomRight()) / 2
        l = (rect.topLeft() + rect.bottomLeft()) / 2
        self.selection_corners[0].setPos(tl)
        self.selection_corners[1].setPos(tr)
        self.selection_corners[2].setPos(br)
        self.selection_corners[3].setPos(bl)
        self.selection_corners[4].setPos(t)
        self.selection_corners[5].setPos(r)
        self.selection_corners[6].setPos(b)
        self.selection_corners[7].setPos(l)

    def setCornerVisibility(self, visible):
        for corner in self.selection_corners:
            corner.setVisible(visible)

    def paintEvent(self, event: QPaintEvent):

        painter = QPainter(self)

        if (self.locked):

            loading = self.buttons_view.state is ProgramState.LOADING

            color = Qt.GlobalColor.red

            if loading:
                color = Qt.GlobalColor.yellow

            painter.setPen(QPen(color,
                           4, Qt.PenStyle.DashLine))
            painter.drawRect(
                self.selected_area.rect().adjusted(-2, -2, 2, 2))
            return

        painter.setPen(Qt.PenStyle.NoPen)
        # set the brush color with alpha to 0

        background_rect = QRectF(self.rect())
        mask_rect = self.selected_area.rect()

        # Create a new path that excludes the area of the original rectangle
        exclude_path = QPainterPath()
        exclude_path.addRect(background_rect)
        exclude_path.addRect(mask_rect.normalized())
        painter.setClipPath(exclude_path, Qt.ClipOperation.IntersectClip)
        painter.setBrush(QColor(0, 0, 0, 128))
        painter.drawRect(self.rect())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.closeApp()

    def closeApp(self):
        self.close()
        app.quit()

    def mousePressEvent(self, event: QMouseEvent):

        if event.buttons() == Qt.MouseButton.LeftButton:
            self.start_pos = event.pos()
            clicked_items = self.selection_view.items(event.pos())

            clickedItem = None
            for item in clicked_items:
                if isinstance(item, CornerItem):
                    clickedItem = item
                    break

            if clickedItem:
                self.clicked_corner = clickedItem

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):

        current_pos = QPointF(event.pos())
        corner = self.clicked_corner
        rect = self.selected_area.rect()

        self.buttons_view.setVisible(False)

        if corner and rect:

            if corner.index == 0:
                rect.setTopLeft(current_pos)
            elif corner.index == 1:
                rect.setTopRight(current_pos)
            elif corner.index == 2:
                rect.setBottomRight(current_pos)
            elif corner.index == 3:
                rect.setBottomLeft(current_pos)
            elif corner.index == 4:
                rect.setTop(current_pos.y())
            elif corner.index == 5:
                rect.setRight(current_pos.x())
            elif corner.index == 6:
                rect.setBottom(current_pos.y())
            elif corner.index == 7:
                rect.setLeft(current_pos.x())

            self.selected_area.setRect(rect.normalized())
            self.updateCornerPositions()
            self.update()

        else:
            rect = QRectF()
            rect.setTopLeft(QPointF(self.start_pos))
            rect.setBottomRight(QPointF(current_pos))

            self.selected_area.setRect(rect.normalized())
            self.updateCornerPositions()
            self.update()

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):

        width = self.selected_area.rect().width()
        height = self.selected_area.rect().height()

        if abs(width) < 20 or abs(height) < 20:
            self.selected_area.setRect(QRectF())
            self.update()
        else:
            rect = self.selected_area.rect()
            self.buttons_view.update(rect)
            self.buttons_view.setVisible(True)


class View(wgs.QGraphicsView):
    def __init__(self, scene, window):
        super().__init__()
        self.setScene(scene)
        self.setFrameStyle(0)
        self.viewport().setAutoFillBackground(False)
        self.mainwindow = window
        self.setStyleSheet("background-color: transparent")
        self.hovering_corner = None

    def mouseReleaseEvent(self, event):
        event.ignore()

    def mousePressEvent(self, event):
        event.ignore()

    def mouseMoveEvent(self, event):

        items = self.items(event.pos())

        self.hovering_corner = None

        for item in items:
            if isinstance(item, CornerItem):
                self.hovering_corner = item
                break

        if self.hovering_corner:
            self.setCursor(self.hovering_corner.cursor)
            event.accept()

        else:
            self.unsetCursor()
            event.ignore()


class CornerItem(wgs.QGraphicsRectItem):

    def __init__(self, cursorType, index):
        super().__init__()

        self.cursor_types = [

            # Corners
            Qt.CursorShape.SizeFDiagCursor,  # Top-left corner
            Qt.CursorShape.SizeBDiagCursor,  # Top-right corner

            # Edges
            Qt.CursorShape.SizeVerCursor,  # Vertical Edges
            Qt.CursorShape.SizeHorCursor,  # Horizontal Edges
        ]

        self.edge_size = 15
        self.corner_size = 25
        self.index = index
        self.setAcceptHoverEvents(True)
        self.cursor_index = cursorType
        self.cursor = self.cursor_types[cursorType]
        self.setBrush(Qt.GlobalColor.black)
        self.setPen(QPen(Qt.GlobalColor.white, 4, Qt.PenStyle.SolidLine))

        self.setVisible(False)

        if (self.cursor_index > 1):
            self.setRect(QRectF(-self.edge_size/2, -
                         self.edge_size/2, self.edge_size, self.edge_size))
        else:
            self.setRect(QRectF(-self.corner_size/2, -
                         self.corner_size/2, self.corner_size, self.corner_size))


os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"


if __name__ == '__main__':

    app = wgs.QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setQuitOnLastWindowClosed(False)
    mw = MainWindow()
    mw.show()
    app.exec()
