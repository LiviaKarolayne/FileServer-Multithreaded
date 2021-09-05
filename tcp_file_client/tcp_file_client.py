#Variables
#SERVER                    - server ip
#PORT                      - connection port
#FOLDER_PATH               - reference folder containing the download files
#shutdown_command          - reference command to exit the program
#sock                      - object representing the socket of the established connection
#file_name                 - required file name
#file_name_length          - required file size
#file_initial_position     - initial position of the required file
#file_maximum_number_bytes - maximum size to read from required file
#flag                      - has the status of the download sent by the server. Reference values:
                           #0   - File transferred successfully
                           #510 - Insistent file
                           #520 - file does not have read permission
                           #530 - file read error
                           #410 - Reported position does not exist in reference file
                           #450 - connection closed on client
                           
#data_record_length        - amount of data that must be transferred

#Functions
#is_number               -
#validate_numeric_option -
#check_if_folder_exists  - check if the download folder exists. Return: True/False
#create_download_folder  - creates the reference folder for downloads if it does not exist
#open_server_connect     - open a connection and wait for a client to respond. Return: socket object
#close_server_connect    - closes the connection with the client
#send_packaged_data      - sends data to the server
#send_data_string        - sends string data to server
#receive_unpacked_data   - receive server data
#receive_data_string     - receive server string data
#receive_data_byte       - receive byte data to server

#set_path_to_save_files  - sets a default path where download files will be saved. Return: reference file name
                          #Variáveis:
                          #file_name   - filename size for download
                          #folder_path - reference folder containing the download files
                          #folders     - has the number of folders the file has

#write_file              - save the file to the default download folder. Return: reference file name
                          #Variáveis:
                          #file_name   - filename size for download
                          #folder_path - reference folder containing the download files
                          #file_path   - path where file should be written
                          #data        - respective contents of the file

import socket, struct, os, re

def is_number(string):
    eValida = bool(re.match(r'^[0-9]*$', string))   
    return eValida

def validate_numeric_option(message):
    option = input(message)
    while not is_number(option):
        print('*** Invalid option, type another')
        option = input(message)
    option = int(option)
    return option

def check_if_folder_exists(folder_path):
    if os.path.isdir(folder_path):
        return True
    else:
        return False

def create_download_folder(folder_path):
    if not check_if_folder_exists(folder_path): #check if the folder already exists
        os.mkdir(folder_path)

def open_server_connect(server, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #open a tcp connection
    sock.connect((SERVER, PORT)) #set the correct data for connection
    print('*** Starting connection with server')
    return sock

def close_server_connect(sock):
    sock.close
    print('*** Closing connection to server\n\n')

def send_packaged_data(struct_type, sock, data):
    data = struct.pack(struct_type, data)
    sock.sendall(data)
    print('*** data sent to', SERVER)

def send_data_string(sock, data):
    sock.sendall(data.encode('utf-8'))
    print('*** data sent to', SERVER)

def receive_unpacked_data(struct_type, sock, byte_length):
    data = struct.unpack(struct_type, sock.recv(byte_length))[0]
    print('***', data, 'received')
    return data

def receive_data_string(sock, byte_length):
    data = sock.recv(byte_length).decode('utf-8')
    print('***', data, 'received')
    return data

def receive_data_byte(sock, byte_length):
    data = sock.recv(byte_length)
    print('***', data, 'received')
    return data

def set_path_to_save_files(file_name, folder_path):
    folders = file_name.split('/')
    folders_number = len(folders)
    file_name = folder_path+'/'+folders[folders_number-1] #extracts the reference file name and inserts it in the downloads folder
    return file_name

def write_file(sock, file_name, folder_path):
    try:
        file_path = set_path_to_save_files(file_name, folder_path) #resets download file reference path
        with open(file_path, 'wb') as file:
            data = receive_data_byte(sock, 4096) #read the first 4096 bytes of the file
            while data:
                file.write(data) #inserts the respective data from the reference file in the downloads folder
                data = receive_data_byte(sock, 4096) #read the respective 4096 bytes of the file
        print('***',file_name,'file transferred successfully')    
    except:
        print('*** Cannot open this file')

SERVER = '127.0.0.1'
PORT = 12345
FOLDER_PATH = 'Downloads'
shutdown_command = 'exit'

create_download_folder(FOLDER_PATH)

while True:      
    sock = open_server_connect(SERVER, PORT)
    
    #asks the user for data about the file that will be downloaded
    file_name = input(f'Enter the name of the file to be downloaded or enter "{shutdown_command}" to exit: ')

    if (file_name.lower() == shutdown_command): #exits the program if user types "exit"
        send_packaged_data('h', sock, 3)
        send_data_string(sock, '450')
        break
    
    file_name_length = (len(file_name))
    file_initial_position = validate_numeric_option('Enter the position of the file where the download should start: ')
    file_maximum_number_bytes = validate_numeric_option('Enter the maximum amount, in bytes, that should be downloaded from this file. Put 0 if this value is unlimited: ')

    send_packaged_data('h', sock, file_name_length)
    send_data_string(sock, file_name)
    send_packaged_data('q', sock, file_initial_position)
    send_packaged_data('q', sock, file_maximum_number_bytes)
    
    flag = receive_data_string(sock, 1)

    #check how the download took place      
    if flag == '0':
        data_record_length = receive_unpacked_data('q', sock, 8)
        print('*** 0: the', file_name, 'file will have', data_record_length, 'bytes')
        
        write_file(sock, file_name, FOLDER_PATH)
        print('*** The', file_name, 'file was transferred to in the', FOLDER_PATH, 'folder')
        
    elif flag == '510':
        print('*** 510:',file_name,'file does not exist')
    elif flag == '520':
        print('*** 520:',file_name,'file does not have read permission')
    elif flag == '530':
        print('*** 530: could not read', file_name, 'file')
    elif flag == '410':
        print('*** 410:',file_name,'is smaller than necessary to start')
        
    close_server_connect(sock)
