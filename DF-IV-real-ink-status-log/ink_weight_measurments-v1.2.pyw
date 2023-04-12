import pyads
import csv
from datetime import datetime
import schedule
import time
from twilio.rest import Client


flag = 0
def alert(CI, DI):
    # Twilio account details
    account_sid = 'account_sid'
    auth_token = 'auth_token'
    client = Client(account_sid, auth_token)
    recipients = ['+321321321','+123123123']
    CI = CI*27/50
    DI = DI*160/177
    if CI<=55:
        print('CI')
        for recipient in recipients:
            message = client.messages.create(
                body=f'Hello from DF-IV NNN! please refil CI i`m almost dry, curent amount {CI}ml!',
                from_='+321654987', #twilio number
                to=recipient
            )
           # print(message.sid)
    elif DI<=50:
        print('DI')
        for recipient in recipients:
            message = client.messages.create(
                body=f'Hello from DF-IV NNN! please refil DI i`m almost dry, curent amount {DI}ml!',
                from_='+321654987', #twilio number
                to=recipient
            )
          #  print(message.sid)


def task():

    """
    Reads data from a PLC and writes it to a CSV file every 20 seconds.

    Reads values from the PLC using the pyads library, including the weight of two tanks,
    the status of various sensors and valves, and a minimum value stored in a separate file.
    The values are written to a CSV file located at "csv_file_path". If the file does not exist,
    it will be created. If a "minimum_param.txt" file does not exist, it will be created with a default
    value of 999. The minimum value is updated as new readings are taken, and written to the file.

    Raises:
        FileNotFoundError: If the file at csv_file_path cannot be found.

    Returns:
        None
    """
    # Define the path to the CSV file
    # you can specify any path you want for the output file.
    csv_file_path = "C:\\Users\\Dragonfly\\Documents\\data.csv"

    # connect to plc and open connection
    # you have to put an right IP from your PC 
    # no need in update the port number.
    plc = pyads.Connection('9.99.999.99.1.1', 888)
    plc.open()
    try:
        with open("C:\\Users\\Dragonfly\\Documents\\minimum_param.txt", "r", encoding="utf-8") as file:
            minimum = int(file.read())
        # print(minimum)
    except FileNotFoundError:
        with open("C:\\Users\\Dragonfly\\Documents\\minimum_param.txt", "w", encoding="utf-8") as file:
            file.write("999")
        minimum = 999
        # print(minimum)
    # read int value by name
    CI_main_tank = plc.read_by_name("LoadCell.nValue_DINT[1]")
    DI_main_tank = plc.read_by_name("LoadCell.nValue_DINT[2]")
    if CI_main_tank>55 and DI_main_tank>55:
        flag = 0
    elif not flag:
        flag = 1
        alert(CI_main_tank,DI_main_tank)
    # read values by group and offset: 
    # first value is group value in hex 
    # second value is offset in hex
    # to get better explanation go to "readme.txt" file.
    # CI_secondary_high = plc.read(0xF021, 0xC2, pyads.PLCTYPE_BOOL)
    # DI_secondary_high = plc.read(0xF021, 0xE2, pyads.PLCTYPE_BOOL)
    # seperator_full = plc.read(0xF021, 0x321, pyads.PLCTYPE_BOOL)
    # seperator_valve = plc.read(0xF031, 0x1C0, pyads.PLCTYPE_BOOL)
    
    # make sure the minimum value stored in excell
    if minimum > CI_main_tank:
        minimum = CI_main_tank
        with open("C:\\Users\\Dragonfly\\Documents\\minimum_param.txt", "w", encoding="utf-8") as file:
            file.write(str(minimum))
    # write int value by name
    # plc.write_by_name("GVL.int_val", i)
    # print(f'The value of the variable is {i}')

    # get the current date and time
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with open(csv_file_path, mode="a", newline="") as csv_file:
            csv_writer = csv.writer(csv_file, encoding="utf-8")
            csv_writer.writerow([current_time, CI_main_tank, DI_main_tank])
            # can be added also int(CI_secondary_high), int(
            #    DI_secondary_high), minimum, int(seperator_full), int(seperator_valve)
    except FileNotFoundError as error:
        print('File not found, error message ' + error)
    # close connection
    plc.close()
    csv_file.close()

# define what the repeat time for the readings in seconds.
# can be changed to minutes or hours "schedule.every(20).minutes.do(task)"
schedule.every(20).seconds.do(task)

while True:
    schedule.run_pending()
    time.sleep(1)
