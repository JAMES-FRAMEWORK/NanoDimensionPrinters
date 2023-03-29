import os
import pandas as pd
import datetime
import zipfile
import re
import shutil
from PyQt6 import QtCore, QtGui, QtWidgets
import sys
from output import Ui_MainWindow


def get_logs_list(folder):
    """Return a list of logs files in the given folder.

    Args:
        folder (str): The path to the folder containing logs files.

    Returns:
        list: A list of logs files in the given folder.
    """
    logs_list = []
    try:
        for filename in os.listdir(folder):
            if not ".log" in filename:
                continue
            else:
                logs_list.append(filename)
    except FileNotFoundError:
        ui.textBrowser.append(f"No such folder: {folder}")
    return logs_list


def get_source_path(folder, PJName, recipename):
    """
    Returns the path of the recipe folder for a given print job and recipe name.

    Args:
        folder (str): The path of the directory to search for print job logs.
        PJName (str): The name of the print job.
        recipename (str): The name of the recipe.

    Returns:
        str: The path of the recipe folder if found, otherwise an empty string.
    """
    for filename in os.listdir(folder):
        if not PJName in filename or '.log' in filename:
            continue
        if recipename in os.listdir(folder+'/'+filename+'/'+'Recipe'):
            return folder+'/'+filename+'/'+'Recipe'

    return ''


def open_file(path):
    """
    Open a file located at the given path and read its contents using pandas.

    Args:
    path (str): the path to the file to be opened

    Returns:
    dict: A dictionary representing the contents of the file
    """
    filename = "pcbj.info"
    data = pd.read_json(path + "/" + filename, orient='index').to_dict()
    return data


def save_file(log, folder):
    """Save the log data to a CSV file in the specified folder.

    Args:
        log (list): A list of dictionaries containing log data.
        folder (str): The folder path where the CSV file will be saved.

    Returns:
        tuple: A tuple containing a dictionary of the log data and the name of the CSV file.

    Raises:
        Exception: If the file is already open, the function will raise an exception.
    """
    filename = "statistics.csv"
    df = pd.DataFrame(log)
    try:
        df.to_csv(folder+'/'+filename, index=False)
    except FileExistsError:
        raise Exception(
            'File already open, please close the file and try again')
    return dict, filename


def get_te_file(path, filename):
    """Searches for a file in a given path with a specific filename and 'PrintSeq' in its name.

    Args:
        path (str): Path to the directory where the file should be searched.
        filename (str): Name of the file to be searched.

    Returns:
        str: Name of the file if found, otherwise None.
    """
    try:
        for file in os.listdir(path):
            if not filename in file:
                continue
            if not 'PrintSeq' in file:
                continue
            return file
    except FileNotFoundError:
        print(f"Directory {path} not found.")
        return None


def get_folder_log_path(folder, filename):
    """
    Given a folder and filename, returns the full path to the folder containing 
    the log file associated with the filename. Returns 'no such folder' if the 
    specified folder does not exist.

    Args:
    - folder (str): path to the folder to search for the log file
    - filename (str): name of the file whose associated log file we want to find

    Returns:
    - new_folder (str): path to the folder containing the log file associated 
                        with the given filename, or 'no such folder' if the 
                        specified folder does not exist

    Raises:
    - Exception: if there was an error accessing the specified folder

    """

    try:
        new_folder = ''
        for file in os.listdir(folder):
            if new_folder != '':
                break
            if '.log' in file:
                continue
            if not filename in re.sub('[^a-zA-Z ]+', '', file.replace('.log', '')):
                continue
            new_folder = folder + '/' + file
        if new_folder == '':
            return 'Log file not found.'
        return new_folder
    except FileNotFoundError:
        ui.textBrowser.append('no such folder')
        return 'no such folder'


def time_estimation_calc(TE_logs, file):
    """
    Calculates the time estimation based on the start and end times in the given file.

    Args:
        TE_logs (str): Path to the folder containing the TE log file.
        file (str): Name of the TE log file.

    Returns:
        str: Time estimation in the format of HH:MM:SS.

    Raises:
        FileNotFoundError: If the specified file or folder does not exist.
        IndexError: If the file is empty or has fewer than 2 lines.
        ValueError: If the start and end times cannot be parsed from the file.
    """
    try:
        with open(TE_logs+'/'+file) as f:
            f = f.readlines()
        if len(f) < 2:
            raise IndexError("File is empty or has fewer than 2 lines")
        start_time = f[0]
        end_time = f[len(f)-1]
        temp1 = re.search(
            '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-2][0-9]\:[0-6][0-9]\:[0-6][0-9]', start_time)
        temp2 = re.search(
            '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-2][0-9]\:[0-6][0-9]\:[0-6][0-9]', end_time)
        if not temp1 or not temp2:
            raise ValueError("Could not parse start and end times from file")
        time_estimation = datetime.datetime.strptime(end_time[temp2.regs[0][0]:temp2.regs[0][1]], '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(
            start_time[temp1.regs[0][0]:temp1.regs[0][1]], '%Y-%m-%d %H:%M:%S')
        return str(time_estimation)
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            "The " + exc + " file or folder does not exist")


def calculate_percentage(dictionary):
    """
    Calculates the percentage of conductor and insulator slices out of the total number of slices in a dictionary.

    Args:
        dictionary: A dictionary containing the number of conductor, insulator, and total slices.

    Returns:
        The percentage of conductor and insulator slices out of the total number of slices.

    Raises:
        ZeroDivisionError: If the total number of slices is 0.
    """
    conductor_slices = dictionary.get('Conductor Slices', 0)
    insulator_slices = dictionary.get('Insulator Slices', 0)
    total_slices = int(dictionary.get('Total Slices', 0))
    if conductor_slices == '':
        conductor_slices = int(dictionary.get(
            'Conductor Slices', 0).replace('', '0'))
        insulator_slices = int(insulator_slices)
    elif insulator_slices == '':
        insulator_slices = int(dictionary.get(
            'Insulator Slices', 0).replace('', '0'))
        conductor_slices = int(conductor_slices)

    if total_slices == 0:
        raise ZeroDivisionError('Total number of slices is 0.')

    percentage = (conductor_slices + insulator_slices) / total_slices
    return percentage


def save_recipes(log_path):
    """
    Saves recipes to an output folder.

    Args:
        log_path (str): The path to the log folder.

    Returns:
        None
    """
    recipes = []
    for row in log:
        recipe = {}
        exist = 0
        for rec in recipes:
            if row.get('Recipe') in rec.get('name'):
                exist = 1
                break
        if not exist:
            recipe['name'] = row.get('Recipe')
            recipe['PJ name'] = row.get('File Name')
            recipes.append(recipe)
    try:
        os.mkdir('C:/output/recipes')
    except FileExistsError:
        shutil.rmtree('C:/output/recipes')
        os.mkdir('C:/output/recipes')
    for rec in recipes:
        try:
            shutil.copytree(get_source_path(log_path, rec.get('PJ name'), rec.get(
                'name')), 'C:/output/recipes/'+rec.get('name'))
        except FileNotFoundError:
            print("Error: source path not found.")
            return
    return


def create_output_folder(path):
    """
    Creates a new folder in the output directory with the given path.

    Args:
    path (str): The name of the folder to be created.

    Raises:
    Exception: If the folder cannot be created or deleted.

    Returns:
    None
    """
    try:
        os.mkdir('C:/output/' + path)
    except FileExistsError:
        shutil.rmtree('C:/output/' + path)
        os.mkdir('C:/output/' + path)
    return


def find_recipe(log_folder):
    """
    Finds the recipe name for a given PCB job file in the specified log folder.

    Args:
        log_folder (str): Path to the folder containing the PCB job files.

    Returns:
        str: The name of the recipe used for the PCB job file, or False if the recipe cannot be found.
    """
    for pcbjc in os.listdir(log_folder):
        if 'Recipe' in pcbjc:
            return os.listdir(log_folder + '/' + pcbjc)[0]

        if not '.pcbjc' in pcbjc:
            continue

        try:
            archive = zipfile.ZipFile(log_folder + '/' + pcbjc, 'r')
            imgfile = archive.open('pcbj.info')
            data = pd.read_json(imgfile, orient='index').to_dict()
            return data[0].get('Recipe')
        except PermissionError:
            ui.textBrowser.setPlainText('No permision to open the log files')
            return False
        except FileNotFoundError:
            return False


def real_time_calculation(log_dict, total_time):
    """
    Calculates the time wasted for a Print Job and updates the total time.

    Args:
        log_dict (dict): A dictionary containing the start and end times of a PJ.
        total_time (int): The total time spent on all PJ`s.

    Returns:
        time_wasted (datetime.timedelta): The time wasted on the PJ.
        total_time (int): The updated total time spent on all PJs.
    """
    if not log_dict.get('End Time') or not log_dict.get('StartTime'):
        ui.textBrowser.append(
            'Start time or end time does not exist for project: ' + log_dict['File Name'])
        return False

    time_wasted = datetime.datetime.strptime(
        log_dict['End Time'], '%Y-%m-%d__%H-%M-%S') - datetime.datetime.strptime(log_dict['StartTime'], '%Y-%m-%d__%H-%M-%S')

    if time_wasted.days:
        total_time += abs(time_wasted.days * 86400)

    total_time += abs(time_wasted.seconds)
    return time_wasted, total_time


def logic():
    '''main function to collect logs and create list of dictionaries , each dict represent print job.

    no input needed

    few out : output folder in C drive with statistics and all different recipes.
    '''
    ui.textBrowser.setPlainText('collecting logs . . . ')
    TELogs = 'C:/DragonFly/Logs/TimeEstimationLogs'
    total_time = 0
    folder = 'C:/DragonFly/PrintLogs'
    interested = ['File Name', 'Recipe', 'DragonflyPC', 'Initial Time Estimation', 'StartTime', 'End Time',  'Conductor Slice Thickness',
                  'Insulator Slice Thickness', 'Tray Temp', 'Resolution', 'Insulator Slices', 'Conductor Slices', 'Total Slices', 'Percentage', 'Finish Status', 'Time spent']
    file_list = get_logs_list(folder)
    #
    for filename in file_list:
        log_dict = dict()
        for key in interested:
            log_dict[key] = ''
        try:
            with open(folder+'/'+filename) as f:
                f = f.readlines()
        except FileNotFoundError:
            ui.textBrowser.append('no such folder' + filename)
        ### add file name to dict ###
        log_dict["File Name"] = filename[re.search(
            '[a-zA-Z]+_* *[a-zA-Z]+|[a-zA-Z]+', filename).regs[0][0]:re.search('[a-zA-Z]+_* *[a-zA-Z]+|[a-zA-Z]+', filename).regs[0][1]]
        ### get Time estimation file ###
        time_estimation_file = get_te_file(TELogs, log_dict["File Name"])
        if time_estimation_file:
            log_dict['Initial Time Estimation'] = time_estimation_calc(
                TELogs, time_estimation_file)
        ### add Recipe name to Dict ###
        log_older = get_folder_log_path(folder, log_dict["File Name"])
        if not log_older:
            continue
        recipe = find_recipe(log_older)
        if recipe:
            log_dict['Recipe'] = recipe
        else:
            log_dict['Recipe'] = 'no pcbjc file'
            ui.textBrowser.setPlainText('no pcbjc file')
        ############## end #################
        for line in f:
            if line == "\n" or "-----" in line:
                continue
            key, value = line.split(':\t')
            value = value.rstrip()
            for inter in interested:
                if inter in key:
                    if not log_dict.get(key):
                        log_dict[inter] = value
        ############# add actual Printing time ############################

        time_wasted, total_time = real_time_calculation(log_dict, total_time)
        if not time_wasted:
            continue
        log_dict['Percentage'] = round(calculate_percentage(log_dict), 4)*100
        log_dict['Time spent'] = str(time_wasted)
        # point to add more calculations for logging
        log.append(log_dict)

    ui.textBrowser.setPlainText(str(datetime.timedelta(seconds=total_time)))

    df = pd.DataFrame(data=log)
    for key in interested:
        if key == 'Time spent':
            log_dict[key] = str(datetime.timedelta(seconds=total_time))
            continue
        log_dict[key] = ''
    # last_row=[' ' for i in range(len(log_dict)-1)] + ['Total Working time'] + [str(datetime.timedelta(seconds=total_time))]
    df2 = pd.DataFrame(data=log_dict, index=[len(log)])
    df = df.append(df2, ignore_index=True)
    create_output_folder('')
    _, filename = save_file(log, 'C:/output/')
    save_recipes(folder)
    ui.textBrowser.append('you run '+str(len(log))+' print jobs')
    ui.textBrowser.append(
        'the logs are collected correctly\nyou can find them in:\nc://output')


def finish():
    """
    Exit the application.
    """
    sys.exit()


if __name__ == '__main__':
    log = []

    # create application
    app = QtWidgets.QApplication(sys.argv)
    # create form and init UI
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    # Hook logic

    ui.pushButton.clicked.connect(logic)
    ui.pushButton_2.clicked.connect(finish)

    # Run main loop
    sys.exit(app.exec())
