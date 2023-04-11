import os
import csv
import sys
from output import Ui_LogercollectorJAMES
import pandas as pd
import datetime
import zipfile
import re
import shutil
from PyQt6 import QtCore, QtGui, QtWidgets




def get_logs_list(path):
    """
    collect logs from a specified path
    returns list with names of PJ.
    """
    file_list = []
    for filename in os.listdir(path):
        file_list.append(filename)

    return file_list


def exclude_alert_id(data):
    """
    Excludes the "alert_id" field from each dictionary in a list of dictionaries.

    Args:
    data (list): A list of dictionaries, each representing a data point.

    Returns:
    list: A list of dictionaries, each representing a data point without the "alert_id" field.
    """
    try:
        return [{k: v for k, v in d.items() if "ALERT_ID" not in k} for d in data]
    except Exception as error:
        print("An error occurred:", error)
        return None


def save_dict_to_csv(data, filename):
    """
    Saves a list of dictionaries to a CSV file.

    Args:
        data (list[dict]): The data to save as a CSV file.
        filename (str): The name of the CSV file to save.

    Raises:
        IOError: If the file cannot be opened or written to.
    """
    data = exclude_alert_id(data)
    try:
        with open(filename, 'a', newline='', encoding='utf-8') as csv_file:
            fieldnames = data[0].keys()
            writer = csv.DictWriter(csv_file, fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)
    except IOError as error:
        print(f"Error: Could not save file {filename}. {error}")


def logic():
    """
    Collects and processes print job logs from a folder, 
    saves the output to a file, and saves recipe information to a separate file.
    Parameters:
    None.
    Returns:
    None.
    """
    ui.textBrowser.setPlainText('collecting logs')
    # total_time = 0
    folder = 'C:/DragonFly/Logs/PrintJobStatLogs'
    filename_save = 'C:/DragonFly/Logs/statistics.csv'
    ui.textBrowser.setPlainText(
        'output file save path is: C:/DragonFly/Logs/statistics.csv')
    file_list = get_logs_list(folder)
    data = []
    for filename in file_list:
        try:
            with open(folder+'/'+filename, encoding='utf-8') as file:
                file_content = file.readlines()
                for line in file_content:
                    if not line:
                        continue
                    fields = line.split(' , ')
                    record = {}
                    for field in fields:
                        key, value = field.split('::')
                        record[key] = value
                    data.append(record)
        except FileNotFoundError:
            ui.textBrowser.append('no such folder' + filename)
    save_dict_to_csv(data, filename_save)
    #ui.textBrowser.append('you run '+str(len(log))+' print jobs')


def finish():
    '''here is function that closin the ui and the software itself.'''
    ui.textBrowser.setPlainText('closing ...')
    exit()


if __name__ == '__main__':
    log = []

    # create application
    app = QtWidgets.QApplication(sys.argv)
    # create form and init UI
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_LogercollectorJAMES()
    ui.setupUi(MainWindow)
    MainWindow.show()
    # Hook logic
    ui.pushButton.clicked.connect(logic)
    ui.pushButton_2.clicked.connect(finish)
    # Run main loop
    sys.exit(app.exec())
