from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
import math
import numpy as np
import json
import zipfile
import shutil


class ZipFileReader:
    def __init__(self,file_path):
        self.file_path = file_path
        self.zip_file = None
        self.info_dict = None
        self.start_pos = 0.0
        self.end_pos = 0.0
        self.zip_file = zipfile.ZipFile(self.file_path, 'r')
        with self.zip_file.open('pcbj.info') as info_file:
            self.info_dict = json.load(info_file)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.zip_file is not None:
            self.zip_file.close()

    def read_values(self):
        self.group_axis = float(self.info_dict['PositionInMM'].get('GroupAxis', 0.0))
        self.print_axis = float(self.info_dict['PositionInMM'].get('PrintAxis', 0.0))

        # Read values into float variables
        value1 = float(self.group_axis)
        value2 = float(self.print_axis)

        return value1, value2

    def update_start_pos(self, group_pos, print_pos):
        self.info_dict['PositionInMM']['GroupAxis'] = group_pos
        self.info_dict['PositionInMM']['PrintAxis'] = print_pos
        # self.start_pos = float(new_start_pos)

    def read_last_image(self):
        # self.window = Viewer()
        last_picture = self.zip_file.read(self.zip_file.filelist[len(self.zip_file.filelist)-2])
        ba = QtCore.QByteArray(last_picture)
        img = QtGui.QImage.fromData(ba)
        return QtGui.QPixmap(img)
    
    def update_z_start_pos(self, starting_z_position):
        layers = self.info_dict["Layers"]
        current_z = starting_z_position
        for layer in layers:
            layer["LayerStartPosZInUM"] = current_z
            current_z += layer["Separations"][0]["LayerThicknessUM"]
        self.save()
        #TODO
        pass

    def save(self):
            # Create a temporary file to write the updated ZIP data to
        temp_file_path = self.file_path + '.temp'

        # Open the input ZIP file and the temporary file for writing
        with zipfile.ZipFile(self.file_path, 'r') as input_zip_file, \
            zipfile.ZipFile(temp_file_path, 'w') as temp_zip_file:
            # Iterate over all files in the input ZIP file
            for name in input_zip_file.namelist():
                # If the file is not the one we want to delete, copy it over to the temporary file
                if name != 'pcbj.info':
                    with input_zip_file.open(name) as source_file:
                        temp_zip_file.writestr(name, source_file.read())
            temp_zip_file.writestr('pcbj.info', json.dumps(self.info_dict))

        # Replace the original file with the temporary file
        shutil.move(temp_file_path, self.file_path)
##################################################################################
class RulerLineItem(QtWidgets.QGraphicsLineItem):
    def __init__(self):
        super(RulerLineItem, self).__init__()

        self.defaultWith = 3
        self.width = self.defaultWith
        self.setZValue(100)

        self.pen = QtGui.QPen()  # creates a default pen
        self.pen.setStyle(Qt.SolidLine)
        self.pen.setWidthF(self.width)
        self.pen.setBrush(Qt.yellow)
        self.pen.setCapStyle(Qt.RoundCap)
        self.pen.setJoinStyle(Qt.RoundJoin)
        self.pen.setCosmetic(True)
        self.setPen(self.pen)

        self.x_start,self.y_start = 0,0
        self.x_end,self.y_end = 0,0

        self.length = 0
    
    def setStartPosition(self,point:QtCore.QPoint):
        self.x_start,self.y_start = math.floor(point.x())+0.5,math.floor(point.y())+0.5

    def setEndPosition(self,point:QtCore.QPoint):
        self.x_end,self.y_end = math.floor(point.x())+0.5,math.floor(point.y())+0.5

    def draw(self):
        self.setLine(self.x_start,self.y_start,self.x_end,self.y_end)
        self.show()

    def getLength(self,factorX=1,factorY=1):
        x_delta = (self.x_start-self.x_end)*factorX
        y_delta = (self.y_start-self.y_end)*factorY
        self.length = math.sqrt(x_delta*x_delta+y_delta*y_delta)
        return self.length

class trayRectItem(QtWidgets.QGraphicsRectItem):
    def __init__(self):
        super(trayRectItem, self).__init__()
        self.ResolutionInUM_PrintAxis = 36
        self.ResolutionInUM_GroupAxis = 35.25

        self.pen = QtGui.QPen()  # creates a default pen
        self.pen.setWidth(20)
        self.pen.setStyle(Qt.SolidLine)
        self.pen.setBrush(Qt.gray)
        self.pen.setCapStyle(Qt.RoundCap)
        self.pen.setJoinStyle(Qt.RoundJoin)
        self.setPen(self.pen)

        self.setZValue(-1)

        self.brush = QtGui.QBrush() # creates a QBrush pen
        self.brush.setStyle(Qt.NoBrush)
        self.brush.setColor(Qt.gray)

        self.setBrush(self.brush)

    def setImageSize(self,width,height):
        self.width = width
        self.height = height

    def draw(self):
        xCenter = self.width/2
        yCenter = self.height/2
        trayWidth=200*1000/self.ResolutionInUM_GroupAxis
        trayHeight=200*1000/self.ResolutionInUM_PrintAxis
        self.setRect(xCenter-trayWidth/2,yCenter-trayHeight/2,trayWidth,trayHeight)


class DropGroupItemGroup(QtWidgets.QGraphicsItemGroup):
    def __init__(self):
        super(DropGroupItemGroup, self).__init__()
        self.dropSizeInPixel = 2.2
        self.penCI = QtGui.QPen()  
        self.penCI.setWidthF(0.02)
        self.penCI.setStyle(Qt.SolidLine)
        self.penCI.setBrush(Qt.white)

        self.penDI = QtGui.QPen()  
        self.penDI.setWidthF(0.02)
        self.penDI.setStyle(Qt.SolidLine)
        self.penDI.setBrush(Qt.yellow)

        colorCI = QtGui.QColor(200,200,200,180)
        self.brushCI = QtGui.QBrush() # creates a QBrush pen
        self.brushCI.setColor(colorCI)
        self.brushCI.setStyle(Qt.SolidPattern)
        
        colorDI = QtGui.QColor(237,185,50,180)
        self.brushDI = QtGui.QBrush() # creates a QBrush pen
        self.brushDI.setColor(colorDI)
        self.brushDI.setStyle(Qt.SolidPattern)

    def drawCIDrops(self,items):
        for item in items:
            x = item[1]-self.dropSizeInPixel/2
            y = item[0]-self.dropSizeInPixel/2
            drop = QtWidgets.QGraphicsEllipseItem(x,y,self.dropSizeInPixel,self.dropSizeInPixel)
            drop.setBrush(self.brushCI)
            drop.setPen(self.penCI)
            self.addToGroup(drop)

    def drawDIDrops(self,items):
        for item in items:
            x = item[1]-self.dropSizeInPixel/2
            y = item[0]-self.dropSizeInPixel/2
            drop = QtWidgets.QGraphicsEllipseItem(x,y,self.dropSizeInPixel,self.dropSizeInPixel)
            drop.setBrush(self.brushDI)
            drop.setPen(self.penDI)
            self.addToGroup(drop)


class Viewer(QtWidgets.QGraphicsView):
    mousePress = QtCore.pyqtSignal(QtCore.QPoint)
    mouseMove = QtCore.pyqtSignal(QtCore.QPoint)
    mouseRelease = QtCore.pyqtSignal(QtCore.QPoint)
    wheel = QtCore.pyqtSignal()

    def __init__(self, parent):
        super(Viewer, self).__init__(parent)
        self._zoom = 0

        self._zoomMax = 30
        self._zoomMin = 0.05

        self.ResolutionInUM_PrintAxis = 36
        self.ResolutionInUM_GroupAxis = 35.25

        self._empty = True
        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self._groupGrid = QtWidgets.QGraphicsItemGroup()
        self._RulerLine = RulerLineItem()
        self._tray = trayRectItem()
        self._scene.addItem(self._groupGrid)
        self._scene.addItem(self._photo)
        self._scene.addItem(self._RulerLine)
        self._scene.addItem(self._tray)


        self._mousePressd = False
        self._showGrid = False
        

        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

    def drawTray(self):
        self._tray.ResolutionInUM_PrintAxis = self.ResolutionInUM_PrintAxis
        self._tray.ResolutionInUM_GroupAxis = self.ResolutionInUM_GroupAxis
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        self._tray.setImageSize(rect.width(),rect.height())
        self._tray.draw()
        # self._scene.setSceneRect(10000,10000,-10000,-10000)
        # 
    def drawGrid(self):
        self._scene.removeItem(self._groupGrid)
        self._groupGrid = QtWidgets.QGraphicsItemGroup()
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        width,height=int(rect.width()),int(rect.height())

        pen1 = QtGui.QPen()  # creates a default pen
        pen1.setStyle(Qt.SolidLine)
        pen1.setBrush(Qt.white)
        pen1.setWidthF(0.2)
        pen2 = QtGui.QPen()  # creates a default pen
        pen2.setStyle(Qt.SolidLine)
        pen2.setBrush(Qt.white)
        pen2.setWidthF(0.05)

        for index in range(width+1):
            line = QtWidgets.QGraphicsLineItem(index,0,index,height)
            line.setCacheMode(QtWidgets.QGraphicsItem.DeviceCoordinateCache)
            if index % 10 == 0:
                line.setPen(pen1)
            else:
                line.setPen(pen2)
            self._groupGrid.addToGroup(line)

        for index in range(height+1):
            line = QtWidgets.QGraphicsLineItem(0,index,width,index)
            line.setCacheMode(QtWidgets.QGraphicsItem.DeviceCoordinateCache)
            if index % 10 == 0:
                line.setPen(pen1)
            else:
                line.setPen(pen2)
            self._groupGrid.addToGroup(line)

        self._scene.addItem(self._groupGrid)
        self._groupGrid.hide()

    def getPixmapInNpArray(self):
        pixmap = self._photo.pixmap()
        h = pixmap.size().width()
        w = pixmap.size().height()
        channels_count = 4
        image = pixmap.toImage()
        s = image.bits().asstring(w * h * channels_count)
        arr = np.frombuffer(s, dtype=np.uint8).reshape((w, h, channels_count)) 
        return arr

    def drawDrop(self):
        self.resetDropItemGroup()
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        
        viewrect = self.viewport().rect()
        x,y = viewrect.x(),viewrect.y()
        h,w = viewrect.height(),viewrect.width()
        point1 = self.mapToScene(x,y)
        point2 = self.mapToScene(x+w,y+w)
        x1,y1 = int(point1.x()),int(point1.y())
        x2,y2 = int(point2.x()),int(point2.y())
        img = self.getPixmapInNpArray()

        kernel = np.array([[1,1],[1,1]])
        CiImg = img[:, :, 0].astype(bool).astype("uint8")
        DiImg = img[:, :, 1].astype(bool).astype("uint8")

        # do the convolve
        CiImg_coords = np.argwhere(CiImg == 4)
        DiImg_coords = np.argwhere(DiImg == 4)
        
        CiImg_newCoo = []
        print(x1,y1,x2,y2)
        for coord in CiImg_coords:
            if y1 < coord[0] <y2 and x1 < coord[1] <x2:
                # shift the coodinate for one pixel in x and y
                CiImg_newCoo.append(coord)

        DiImg_newCoo = []
        for coord in DiImg_coords:
            if y1 < coord[0] <y2 and x1 < coord[1] <x2:
                # shift the coodinate for one pixel in x and y
                DiImg_newCoo.append(coord)

        self._dropGroup = DropGroupItemGroup()
        self._scene.addItem(self._dropGroup)
        self._dropGroup.drawCIDrops(CiImg_newCoo)
        self._dropGroup.drawDIDrops(DiImg_newCoo)

    def hasPhoto(self):
        return not self._empty

    def fitInView(self, scale=True):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.hasPhoto():
                self.scaleReset()
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scaleScene(factor)
            # self._zoom = 0

    def scaleReset(self):
        unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
        self.scale(1 / unity.width(), 1 / unity.height())
        self.scale(1,36/35.25)
        # self._RulerLine.resetScale()

    def scaleScene(self,factor):
        self.scale(factor, factor)
        # self._RulerLine.scale(factor)
    
    def getScaleFactor(self):
        unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
        return unity.width()

    def setPhoto(self, pixmap=None):
        if pixmap and not pixmap.isNull():
            self._empty = False
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._photo.setPixmap(QtGui.QPixmap())
        # self.resetDRCItemGroup()
        self.resetDropItemGroup()

    def setNewPhoto(self, pixmap=None):
        self.setPhoto(pixmap)
        self.drawGrid()
        self.drawTray()
        self.fitInView()
        # self._zoom = 0

    def resetDropItemGroup(self):
        try:
            self._scene.removeItem(self._dropGroup)
        except:
            pass
        

    def wheelEvent(self, event):
        self.wheel.emit()
        if self.hasPhoto():
            if event.angleDelta().y() > 0:
                if self.getScaleFactor() <= self._zoomMax:
                    factor = 1.25
                    self.scaleScene(factor)
            else :
                if (self.getScaleFactor() >= self._zoomMin):
                    factor = 0.8
                    self.scaleScene(factor)
        # print(self._zoom)

    def toggleGrid(self):
        self._showGrid = not self._showGrid
        self.update()

    def QPointF2QPoint_floor(self,QPointF):
        return QtCore.QPoint(math.floor(QPointF.x()),math.floor(QPointF.y()))

    def toggleDragMode(self):
        if self.dragMode() == QtWidgets.QGraphicsView.ScrollHandDrag:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        elif not self._photo.pixmap().isNull():
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

    def mousePressEvent(self, event):
        if self._photo.isUnderMouse():
            self._mousePressd = True
            self._RulerLine.setStartPosition(self.mapToScene(event.pos()))
            self.mousePress.emit(self.QPointF2QPoint_floor(self.mapToScene(event.pos())))
        super(Viewer, self).mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if self._photo.isUnderMouse():
            self._RulerLine.setEndPosition(self.mapToScene(event.pos()))
            self.mouseMove.emit(self.QPointF2QPoint_floor(self.mapToScene(event.pos())))
        return super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if self._photo.isUnderMouse():
            self._mousePressd = False
            self.mouseRelease.emit(self.QPointF2QPoint_floor(self.mapToScene(event.pos())))
            self.update()
        return super().mouseReleaseEvent(event)

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        if self.getScaleFactor() > 2 and self._showGrid:
            self._groupGrid.show()
        else:
            self._groupGrid.hide()
        return super().paintEvent(event)

class ImageViewer(QtWidgets.QWidget):
    class _RulerMode():
        pixel = ...
        um = ...

    def __init__(self, parent=None):
        super(ImageViewer, self).__init__(parent)
        self.setupUi()
        self.x_mousePress,self.y_mousePress = 0,0
        self.mousePressd = False
        self.start_position = (0, 0)  # Replace x and y with the bottom-left corner coordinates
        self.pixel_size = (36, 35.25)
        self.RulerMode = self._RulerMode.pixel


    def setupUi(self):
        # self.viewer = Viewer(self)
        self.setAcceptDrops(True)
        self.viewer = ImageOverlap(self)
        # 'update' button
        self.update_button = QtWidgets.QPushButton(self)
        self.update_button.setText('Update SP')
        self.update_button.setFlat(True)
        self.update_button.clicked.connect(self.update)
        # '2nd image button'
        self.load_top_file_button = QtWidgets.QPushButton(self)
        self.load_top_file_button.setText('Load Top File')
        self.load_top_file_button.setFlat(True)
        self.load_top_file_button.clicked.connect(self.load_top_file)
        # 'base file load' button
        self.base_file_button = QtWidgets.QPushButton(self)
        self.base_file_button.setText('load a base file')
        self.base_file_button.setFlat(True)
        self.base_file_button.clicked.connect(self.base_file_load)
        # 'Fit in' button
        self.btn_fitIn = QtWidgets.QPushButton(self)
        self.btn_fitIn.setText('Fit')
        self.btn_fitIn.setFlat(True)
        self.btn_fitIn.clicked.connect(self.fitInView)
        # Button to change from drag/pan to getting pixel info
        self.btn_ruler = QtWidgets.QPushButton(self)
        self.btn_ruler.setText('ruler')
        self.btn_ruler.setFlat(True)
        self.btn_ruler.setCheckable(True)
        self.btn_ruler.clicked.connect(self.toggleRuler)

        self.btn_grid = QtWidgets.QPushButton(self)
        self.btn_grid.setText('grid')
        self.btn_grid.setFlat(True)
        self.btn_grid.setCheckable(True)
        self.btn_grid.clicked.connect(self.toggleGrid)

        self.btn_drop = QtWidgets.QPushButton(self)
        self.btn_drop.setText('drop')
        self.btn_drop.setFlat(True)
        self.btn_drop.clicked.connect(self.drawDrop)
        self.btn_drop.setDisabled(True)

        self.editPixInfo = QtWidgets.QLineEdit(self)
        self.editPixInfo.setReadOnly(True)

        self.viewer.mousePress.connect(self.mousePress)
        self.viewer.mouseMove.connect(self.mouseMove)
        self.viewer.mouseRelease.connect(self.mouseRelease)
        self.viewer.wheel.connect(self.wheel)
        # Arrange layout
        VBlayout = QtWidgets.QVBoxLayout(self)
        HBlayout = QtWidgets.QHBoxLayout()
        Toollayout = QtWidgets.QHBoxLayout()
        HBlayout.setAlignment(QtCore.Qt.AlignLeft)
        
        Toollayout.addWidget(self.btn_fitIn)
        Toollayout.addWidget(self.btn_grid)
        Toollayout.addWidget(self.btn_drop)
        Toollayout.addWidget(self.btn_ruler)
        Toollayout.addWidget(self.base_file_button)
        Toollayout.addWidget(self.load_top_file_button)
        Toollayout.addWidget(self.update_button)

        HBlayout.addLayout(Toollayout)
        HBlayout.addWidget(self.editPixInfo)
        VBlayout.addLayout(HBlayout)
        VBlayout.addWidget(self.viewer)
        VBlayout.setContentsMargins(0, -1, -1, -1)

    def base_file_load(self):
        
        # app = QtWidgets.QApplication([])
        dialog = QtWidgets.QFileDialog()
        dialog.setNameFilter("PCBJC Files (*.pcbjc)")
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
        if dialog.exec_() == QtWidgets.QFileDialog.Accepted:
            file_paths = dialog.selectedFiles()
            self.file_reader = ZipFileReader(file_paths[0])
            self.print_start_pos, self.group_start_pos = self.file_reader.read_values()
            self.viewer.setNewPhoto(self.file_reader.read_last_image())

            # print(self.print_start_pos, self.group_start_pos)
###########################################################

    def load_top_file(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.ReadOnly
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open file you want to align", "", "Images (*.pcbjc);;All Files (*)", options=options)
        if file_name:
            self.viewer.load_top_file(file_name)

    def update(self):
        if self.viewer.top_image_item is not None:
            # Get the current position of the center of the top image
            left_top_x, left_top_y = self.viewer.top_image_item.pos().x(), self.viewer.top_image_item.pos().y()
            rect = self.viewer.top_image_item.boundingRect()
            left_botom_x, left_botom_y = left_top_x, left_top_y + rect.height()
            x,y = 0, self.viewer._photo.pixmap().height()
            pixels_change_x = abs(left_botom_x - x)
            pixels_change_y = abs(left_botom_y - y)
            # Set the new position for the top image
            self.viewer.top_image_item.setPos(left_top_x, left_top_y)

            self.set_new_start_position(pixels_change_x, pixels_change_y)


    def set_new_start_position(self, pixels_change_x, pixels_change_y):
        # dialog = NewStartPositionDialog()
        # if dialog.exec_() == QtWidgets.QDialog.Accepted:
        current_x, current_y = self.group_start_pos, self.print_start_pos   #dialog.get_new_position()
        new_x = current_x + pixels_change_x*0.036
        new_y = current_y + pixels_change_y*0.03525
        output_text = f"Updating start position to ({new_x}, {new_y}) based on a pixel change of ({pixels_change_x}, {pixels_change_y})"
        self.file_reader.update_start_pos(new_x, new_y)
        output_dialog = OutputDialog(output_text=output_text)
        output_dialog.exec_()
        # pass
    def toggleGrid(self):
        self.viewer.toggleGrid()

    def toggleRuler(self):
        self.viewer.toggleDragMode()
        if self.btn_ruler.isChecked() == False:
            self.editPixInfo.setText('')
            self.viewer._RulerLine.hide()

    def fitInView(self):
        self.viewer.fitInView()

    def mousePress(self, pos):
        self.mousePressd = True
        if self.viewer.dragMode()  == QtWidgets.QGraphicsView.NoDrag:
            self.x_mousePress,self.y_mousePress = pos.x(), pos.y()

    def drawDrop(self):
        self.viewer.drawDrop()

    def mouseMove(self, pos):
        if self.viewer.dragMode()  == QtWidgets.QGraphicsView.NoDrag:
            if self.mousePressd == True:
                self.viewer._RulerLine.draw()
                self.editPixInfo.setText('Length %.2f pixel, %.2f um' % (self.viewer._RulerLine.getLength(),self.viewer._RulerLine.getLength(self.viewer.ResolutionInUM_GroupAxis,self.viewer.ResolutionInUM_PrintAxis)))
            else:
                self.editPixInfo.setText('Cursor Position:%d,%d'%(pos.x(),pos.y()))
        

    def mouseRelease(self, pos):
        self.mousePressd = False
            
    def wheel(self):
        if self.viewer.getScaleFactor() >25 and self.viewer.ResolutionInUM_PrintAxis != 36:
            self.btn_drop.setDisabled(False)
        else:
            self.btn_drop.setDisabled(True)

class OutputDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, output_text=""):
        super().__init__(parent)

        # Set up the layout
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        # Add the output label
        self.output_label = QtWidgets.QLabel(output_text)
        self.output_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.layout.addWidget(self.output_label)

        # Add the OK button
        self.ok_button = QtWidgets.QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.layout.addWidget(self.ok_button)

    def get_new_position(self):
        x = float(self.x_text.text())
        y = float(self.y_text.text())
        return x, y

class ImageOverlap(Viewer):
    def __init__(self, parent=None):
        super(ImageOverlap, self).__init__(parent)
        self.top_image_item = None




    def load_top_file(self, file_path):
        if self.top_image_item is not None:
            self.scene().removeItem(self.top_image_item)

        # Create a ZipFileReader object to read the image data
        zip_reader = ZipFileReader(file_path)

        # Read the last image in the zip file
        pixmap = zip_reader.read_last_image()

        # Change the color of the white pixels
        green = QtGui.QColor(0, 255, 0, 255)
        pixmap = QtGui.QImage(pixmap)
        modified_pixmap = self.change_white_pixels(pixmap, green)

        pixmap = QtGui.QPixmap.fromImage(modified_pixmap)

        self.top_image_item = QtWidgets.QGraphicsPixmapItem(pixmap)
        self.top_image_item.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.top_image_item.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.top_image_item.setZValue(1)
        self.top_image_item.setOpacity(0.5)
        self.scene().addItem(self.top_image_item)
    # def load_top_file(self, image_path):
    #     if self.top_image_item is not None:
    #         self.scene().removeItem(self.top_image_item)

    #     image = QtGui.QImage(image_path)

    #     # Convert the image to RGB32 format if it's not already
    #     if image.format() != QtGui.QImage.Format_RGB32:
    #         image = image.convertToFormat(QtGui.QImage.Format_RGB32)

    #     # Change the color of the white pixels
    #     green = QtGui.QColor(0, 255, 0, 255)
    #     modified_image = self.change_white_pixels(image, green)

    #     pixmap = QtGui.QPixmap.fromImage(modified_image)

    #     self.top_image_item = QtWidgets.QGraphicsPixmapItem(pixmap)
    #     self.top_image_item.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
    #     self.top_image_item.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
    #     self.top_image_item.setZValue(1)
    #     self.top_image_item.setOpacity(0.5)
    #     self.scene().addItem(self.top_image_item)


    def change_white_pixels(self, image, new_color):
        white = QtGui.QColor(255, 255, 255)
        for x in range(image.width()):
            for y in range(image.height()):
                color = QtGui.QColor(image.pixel(x, y))
                if color == white:
                    image.setPixelColor(x, y, new_color)
        return image




if __name__ == '__main__':
    import sys
    from qt_material import apply_stylesheet
    app = QtWidgets.QApplication(sys.argv)
    window = ImageViewer()
    window.setGeometry(500, 300, 800, 600)
    apply_stylesheet(app, theme='my_theme.xml')
    window.show()
        # Show file dialog to select an image
    # options = QtWidgets.QFileDialog.Options()
    # options |= QtWidgets.QFileDialog.ReadOnly
    # file_name, _ = QtWidgets.QFileDialog.getOpenFileName(window, "Choose the base layer Image", "", "Images (*.png *.xpm *.jpg *.bmp *.tiff);;All Files (*)", options=options)

    # if file_name:
    #     window.viewer.setNewPhoto(QtGui.QPixmap(file_name))
    # window.viewer.setNewPhoto(QtGui.QPixmap('./testFile/combined_0_Dielectric.base.tiff'))
    # from pcbjcEditor_core import DesignRuleCheck
    import tifffile 
    debug_image = tifffile.imread('./testFile/combined_0_Dielectric.base.tiff')
    CI = debug_image
    # DRC = DesignRuleCheck()
    sys.exit(app.exec_())

