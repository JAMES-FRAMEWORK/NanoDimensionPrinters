# Imports
import zipfile
import os
import sys
import json
import pandas as pd
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QApplication
from UI_Main import Ui_MainWindow


def change_info_file(file_path):
    """
    Extracts the `pcbj.info` file from a zip archive and modifies its contents by removing the 'Recipe' key and the 
    'LayerStartPosZInUM' attribute from each layer. The modified data is then saved back to the archive as 
    'pcbj.info' file. If the archive does not contain a 'pcbj.info' file or if it is in a strange file version 
    (no 'Recipe' parameter), it returns the original data.
    
    Args:
        file_path (str): The full path to the zip archive.
    
    Returns:
        dict: The modified or original data, as a dictionary.
    """
    try:
        archive = zipfile.ZipFile(file_path[0], 'r')
        imgfile = archive.open('pcbj.info')
        data = pd.read_json(imgfile, orient='index').to_dict()
        for layer in data[0]['Layers']:
            layer.pop("LayerStartPosZInUM")
        data[0].pop('Recipe')
        archive.close()
        imgfile.close()
        save_data(file_path[0],data)
    except KeyError:
        ui.textBrowser.setPlainText('strange file version.... ( no Recipe parameter in info file)')
        return data

def save_data(file_path,data):
    '''Saves the given data to the 'pcbj.info' file in the specified ZIP archive file.

Args:
    file_path (str): The path to the ZIP archive file to save the data to.
    data (list): A list of dictionaries representing the data to save to the 'pcbj.info' file.

Returns:
    None
'''
    try:
        temp_path = file_path + '.tmp'
        # Open the original archive and the temporary archive
        with zipfile.ZipFile(file_path, 'r') as original_archive, zipfile.ZipFile(temp_path, 'w') as temp_archive:
            # Iterate over the original archive's files, adding them to the temporary archive,
            # except for the one we want to delete
            for original_file in original_archive.infolist():
                if original_file.filename != 'pcbj.info':
                    temp_archive.writestr(original_file, original_archive.read(original_file.filename))
        os.remove(file_path)
        os.rename(temp_path, file_path)
        archive = zipfile.ZipFile(file_path, 'a')
        archive.writestr('pcbj.info', json.dumps(data[0], indent=4).encode('utf-8'))
        ui.textBrowser.setPlainText('the data saved succesfully')
    except KeyError:
        ui.textBrowser.setPlainText('the data saved succesfully')
        return data

def browse_files():
    """Open a file dialog window to select a file and set the file path as a global variable.

    Returns:
        list: A list containing the file path of the selected file.
    """
    global file_path
    app = QApplication(sys.argv)
    file_dialog = QFileDialog()
    file_dialog.setFileMode(QFileDialog.AnyFile)
    file_dialog.setOption(QFileDialog.DontUseNativeDialog)
    filenames = []
    if file_dialog.exec_():
        filenames = file_dialog.selectedFiles()
    file_path = filenames
    ui.label.setText(file_path[0][-55:])
    return file_path



def logic(path = os.path.dirname(os.path.realpath(__file__))):
    """
    Perform some logic on the file at the specified path.

    Args:
        path: A string representing the path to the file. If not provided, the path of the current file will be used.

    Returns:
        None
    """
    info = change_info_file(path)
    print(info)

def finish():
    """Close the PyQt5 application and exit the program.

    This function is typically called when the user clicks a "Close" or "Exit" button in the application.
    It calls the `QApplication.exec()` method to start the event loop and waits for the application to exit.
    Once the application has exited, the function calls `sys.exit()` to exit the program with the return code 0
    (indicating success).

    """
    sys.exit(app.exec())
# Main Code
if __name__ == '__main__':

    # file_path=''
    # create application
    app = QtWidgets.QApplication(sys.argv)
    # create form and init UI
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    # Hook logic
    ui.pushButton.clicked.connect(browse_files)
    ui.pushButton_2.clicked.connect(lambda: change_info_file(file_path))
    ui.pushButton_3.clicked.connect(finish)
    # Run main loop
    sys.exit(app.exec())


    
    
    
    
    
    