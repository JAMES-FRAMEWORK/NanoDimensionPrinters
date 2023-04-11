# Imports
import zipfile
import os
import sys
import json
import datetime
import pandas as pd
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QApplication
from UI_Main import Ui_MainWindow






def read_resolution(file_path):
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
        global ci_resolution
        global di_resolution
        global machine_resolution
        global path
        archive = zipfile.ZipFile(file_path[0], 'r')
        imgfile = archive.open('pcbj.info')
        data = pd.read_json(imgfile, orient='index').to_dict()
        ci_resolution = data[0]['Separations'][0]['ResolutionInUM']
        di_resolution = data[0]['Separations'][1]['ResolutionInUM']
        ui.textBrowser.setPlainText('the resolution of PJ is: '+str(ci_resolution['PrintAxis']))
        # closing files
        archive.close()
        imgfile.close()
        
        # read the resolution of the printer:

        path = "C:\\DragonFly\\Conf\\MachineCalibration.cfg"
        with open(path, 'r', encoding="utf-8") as file:
            machine_calibration = file.read()
            data = {}
            for line in machine_calibration.split('\n'):
                if line.strip():
                    key, value = line.split('=')
                    data[key] = value
        if data['ConductorSliceThicknessInUMCoupon']<'1':
            machine_resolution = '36'
        else:
            machine_resolution = '18'
        ui.textBrowser.append('machine resolution is: ' + machine_resolution +'\n')


    except KeyError:
        ui.textBrowser.setPlainText('strange file version.... ( no Resolution parameter in info file)')
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


def upgrade_resolution():
    """
    Upgrade the machine resolution parameter value depending on the PJ resolution and log the changes.

    Globals:
        path (str): the path to the configuration file.
        ci_resolution (dict): a dictionary containing the print axis resolution.

    Returns:
        None
    """
    global path
    global ci_resolution


    # get the right time
    now = datetime.datetime.now()
    date_string = now.strftime("%Y-%m-%d %H:%M:%S")
    # Read the file into a Python variable
    with open(path, 'r', encoding="utf-8") as file:
        machine_calibration = file.read()
    data = {}
    for line in machine_calibration.split('\n'):
        if line.strip():
            key, value = line.split('=')
            data[key] = value
    # Update the parameter value depent on the PJ resolution and create a log of ST changes.
    old = data['ConductorSliceThicknessInUMCoupon']
    if float(data['ConductorSliceThicknessInUMCoupon'])<0.8 and ci_resolution['PrintAxis']==36:
        ui.textBrowser.setPlainText('Everything ok you set to 36um resolution, you can print now.')
        
    elif float(data['ConductorSliceThicknessInUMCoupon'])<0.8 and ci_resolution['PrintAxis']==18:
        data['ConductorSliceThicknessInUMCoupon'] = float(data['ConductorSliceThicknessInUMCoupon']) * 4
        ui.textBrowser.setPlainText('machine resolution updated to 18um, you can print now.')
        with open('C:\\DragonFly\\Conf\\ST_changes.cfg', 'a') as f:
            f.write('\nOn '+date_string +' changed from '+ str(old)+'changed to ' +str(data['ConductorSliceThicknessInUMCoupon']))
    elif float(data['ConductorSliceThicknessInUMCoupon'])>0.8 and ci_resolution['PrintAxis']==18:
        ui.textBrowser.setPlainText('machine resolution is already 18um, you can print now.')
         
    elif float(data['ConductorSliceThicknessInUMCoupon'])>0.8 and ci_resolution['PrintAxis']==36:
        data['ConductorSliceThicknessInUMCoupon'] = float(data['ConductorSliceThicknessInUMCoupon']) / 4
        ui.textBrowser.setPlainText('machine resolution updated to 36um, you can print now.')
        with open('C:\\DragonFly\\Conf\\ST_changes.cfg', 'a') as f:
            f.write('\nOn '+date_string +' changed from '+ str(old)+'changed to ' +str(data['ConductorSliceThicknessInUMCoupon']))
    else:
        return
    
    # Write the updated variable back to the file
    config_str = '\n'.join([f"{key}={value}" for key, value in data.items()])

    with open(path, 'w') as f:
        f.write(config_str)
    
def choose_file_and_read_resolution():
    file_path = browse_files()
    read_resolution(file_path)


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
    ui.pushButton.clicked.connect(choose_file_and_read_resolution)
    ui.pushButton_2.clicked.connect(upgrade_resolution)
    ui.pushButton_3.clicked.connect(finish)
    # Run main loop
    sys.exit(app.exec())
