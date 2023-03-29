import os
import pandas as pd
import datetime
import zipfile
import re
import shutil
from PyQt6 import QtCore, QtGui, QtWidgets
import sys
from output import Ui_MainWindow

def getLogsList(folder):
    temp =[]
    try:
        for filename in os.listdir(folder):
            if not ".log" in filename:
                continue
            else:
                temp.append(filename)
                continue
    except:
        ui.textBrowser.append('no such folder'+ folder)
    return temp

def get_source_Path(folder, PJName, recipename):
    temp =[]

    for filename in os.listdir(folder):
        if not PJName in filename or '.log' in filename:
            continue
        if recipename in os.listdir(folder+'/'+filename+'/'+'Recipe'):
            return folder+'/'+filename+'/'+'Recipe'
            
    return ''

def Open_File(path):
    filename = "pcbj.info"
    data = pd.read_json(filename, orient='index')
    data.to_dict()
    return data

def savefile(log, folder):
    filename = "statistics.csv"

    df = pd.DataFrame(log)
    try:
        df.to_csv(folder+'/'+filename,index=False )
    except:
        ui.textBrowser.append('file already open, please close the file and try again')
    return dict, filename

def getTEfile(path, filename):
    for file in os.listdir(path):
        if not filename in file:
            continue
        if not 'PrintSeq' in file:
            continue
        return file
def getFolderLogPath(folder, filename):
    try:
        newFolder = ''
        for fil in os.listdir(folder):
            if not newFolder == '':
                break
            if '.log' in fil:
                continue
            if not filename in re.sub('[^a-zA-Z ]+', '', fil.replace('.log','')):
                continue
            newFolder = folder+'/'+fil
        return newFolder
    except:
        ui.textBrowser.append('no such folder')
        return 'no such folder'
def TimeEstimationCalc(TELogs, file):
    with open(TELogs+'/'+file) as f:
        f = f.readlines()
    start_time = f[0]
    end_Time = f[len(f)-1]
    temp1 = re.search('[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-2][0-9]\:[0-6][0-9]\:[0-6][0-9]',start_time)
    temp2 = re.search('[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-2][0-9]\:[0-6][0-9]\:[0-6][0-9]',end_Time)
    time_Estimation = datetime.datetime.strptime(end_Time[temp2.regs[0][0]:temp2.regs[0][1]], '%Y-%m-%d %H:%M:%S')-datetime.datetime.strptime(start_time[temp1.regs[0][0]:temp1.regs[0][1]], '%Y-%m-%d %H:%M:%S')
    return str(time_Estimation)

def percentage(dict):
    con = dict.get('Conductor Slices')
    ins = dict.get('Insulator Slices')
    if not dict.get('Conductor Slices'):
        con = 0
    if not dict.get('Insulator Slices'):
        ins = 0
    perc = (int(con)+int(ins))/int(dict.get('Total Slices'))
    return perc

def saveRecipes(logPath):
    recipies=[]
    for row in log:
        recipe ={}
        exist = 0
        for rec in recipies:
            if row.get('Recipe') in rec.get('name'):
                exist = 1
                break
        if not exist:
            recipe['name'] = row.get('Recipe')
            recipe['PJ name'] = row.get('File Name')
            recipies.append(recipe)
    try:
        os.mkdir('C:/output/recipies')
        ui.textBrowser.append('output folder created')
    except:
        shutil.rmtree('C:/output/recipies')
        ui.textBrowser.append('output folder deleted')
        os.mkdir('C:/output/recipies')
        ui.textBrowser.append('output folder created')
    for rec in recipies:
        shutil.copytree(get_source_Path(logPath,rec.get('PJ name'),rec.get('name')), 'C:/output/recipies/'+rec.get('name'))

    return

def createOutputfolder(path):
    try:
        os.mkdir('C:/output/'+path)
    except:
        shutil.rmtree('C:/output/'+path)
        os.mkdir('C:/output/'+path)
    return
def logic():
    ui.textBrowser.setPlainText('collecting logs')
    TELogs = 'C:/DragonFly/Logs/TimeEstimationLogs'
    total_time = 0
    folder = 'C:/DragonFly/PrintLogs'
    interested=['File Name','Recipe', 'DragonflyPC', 'Initial Time Estimation','StartTime', 'End Time',  'Conductor Slice Thickness', 'Insulator Slice Thickness', 'Tray Temp', 'Resolution', 'Insulator Slices', 'Conductor Slices', 'Total Slices', 'Percentage', 'Finish Status', 'Time spent']
    file_list = getLogsList(folder)
    for filename in file_list:
        log_dict = dict()
        for key in interested:
            log_dict[key] = ''
        try:
            with open(folder+'/'+filename) as f:
                f = f.readlines()
        except:
            ui.textBrowser.append('no such folder' + filename)
        ### add file name to dict ###
        log_dict["File Name"] = filename[re.search('[a-zA-Z]+_* *[a-zA-Z]+|[a-zA-Z]+', filename).regs[0][0]:re.search('[a-zA-Z]+_* *[a-zA-Z]+|[a-zA-Z]+', filename).regs[0][1]]
        ### get Time estimation file ###
        Time_Estimation_file = getTEfile(TELogs,log_dict["File Name"])
        if Time_Estimation_file:
            log_dict['Initial Time Estimation'] = TimeEstimationCalc(TELogs, Time_Estimation_file)
        ### add Recipe name to Dict ###
        logFolder = getFolderLogPath(folder, log_dict["File Name"])
        if not logFolder:
            continue
        for PCBJC in os.listdir(logFolder):
            if 'Recipe' in PCBJC:
                log_dict['Recipe'] = os.listdir(logFolder+'/'+PCBJC)[0]
                break
            if not '.pcbjc' in PCBJC:
                continue
            try:
                archive = zipfile.ZipFile(logFolder+'/'+PCBJC, 'r')
                imgfile = archive.open('pcbj.info')
                data = pd.read_json(imgfile, orient='index').to_dict()
                log_dict['Recipe'] = data[0].get('Recipe')
            except:
                log_dict['Recipe'] = 'no pcbjc file'
                ui.textBrowser.setPlainText('no pcbjc file')
        ############## end #################
        for line in f:
            if line == "\n" or "-----" in line:
                continue
            key,value = line.split(':\t')
            value = value.rstrip()
            for inter in interested:
                if inter in key:
                    if not log_dict.get(key):
                        log_dict[inter] = value
        ############# add actual Printing time #############################
        if not log_dict.get('End Time') or not log_dict.get('StartTime'):
            ui.textBrowser.append('start time or end time not exicst for PJ: '+log_dict['File Name'])
            continue
        timeWasted = datetime.datetime.strptime(log_dict['End Time'], '%Y-%m-%d__%H-%M-%S')-datetime.datetime.strptime(log_dict['StartTime'], '%Y-%m-%d__%H-%M-%S')
        if timeWasted.days:
            total_time += abs(timeWasted.days*86400)
        total_time += abs(timeWasted.seconds)
        log_dict['Percentage'] = round(percentage(log_dict),4)*100
        log_dict['Time spent'] = str(timeWasted)
        # point to add more calculations for logging
        log.append(log_dict)

    ui.textBrowser.setPlainText(str(datetime.timedelta(seconds=total_time)))
    _, filename = savefile(log, 'C:/output/')
    df = pd.read_csv('C:/output/'+filename)
    for key in interested:
        if key == 'Time spent':
            log_dict[key] = str(datetime.timedelta(seconds=total_time))
            continue
        log_dict[key] = ''
    # last_row=[' ' for i in range(len(log_dict)-1)] + ['Total Working time'] + [str(datetime.timedelta(seconds=total_time))]
    df2 = pd.DataFrame(data=log_dict, index = [len(log)])
    df = df.append(df2, ignore_index=True)
    createOutputfolder('')
    df.to_csv('C:/output/'+filename, index=False)
    saveRecipes(folder)
    ui.textBrowser.append('you run '+str(len(log))+' print jobs')
    ui.textBrowser.append('the logs are collected correctly\nyou can find them in:\nc://output')
def finish():
    """
    Exit the application.
    """
    exit()


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

    ui.pushButton.clicked.connect( logic )
    ui.pushButton_2.clicked.connect( finish )
    
    #Run main loop
    sys.exit(app.exec())
    
 