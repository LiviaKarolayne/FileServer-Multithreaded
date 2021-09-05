#Variables
#CURRENT_DIRECTORY_PATH - real path of this file
#SERVER                 - server ip
#PORT                   - connection port
#FOLDER_PATH            - reference folder containing the download files
#sock                   - object representing the socket of the established connection
#connection             - object representing the established connection
#adderess               - client address
#thread                 - object that represents the thread

#Functions
#folder_exists                      - check if the download folder exists. Return: True/False
#create_download_folder             - creates the reference folder for downloads if it does not exist
#path_exists                        - check if a file path exists. Return: True/False
#is_file                            - check if there is a file. Return: True/False
#has_read_permission                - check if a file has read permission. True/False
#is_valid_initial_position          - check if the entered start position is valid. True/False
#validate_file_maximum_number_bytes - modifies the maximum invalid value to be read from a file

#read_file                          - read the contents of the file to be transferred. Return: all_data
                                    #variables:
                                    #file_name - file name for download
                                    #all_data  - complete content of the file to be transferred
                                    #data      - respective contents of the file

#open_client_connect                - open a connection and wait for a client to respond. Return: socket object
#close_client_connect               - closes the connection with the client
#open_accept_client_connection      - accept a connection with a client
#close_accept_client_connection     - closes the connection that was accepted by a client
#client_connection_is_open          - check if the client has closed the connection
#receive_unpacked_data              - receive client data
#receive_data_string                - receive client string data
#send_packaged_data                 - sends data to the client
#send_data_string                   - sends string data to client
#send_data_byte                     - sends byte data to client

#main                               - starts program processing logic
                                    #variables:
                                    #connection                - object representing the established connection
                                    #adderess                  - client address
                                    #file_name_length          - required file size
                                    #file_name                 - required file name
                                    #file_initial_position     - initial position of the required file
                                    #file_maximum_number_bytes - maximum size to read from required file
                                    #file_length               - transferred file size
                                    #all_data                  - data to be sent to the client

import socket, threading, struct, os

def folder_exists(folder_path):
    if os.path.isdir(folder_path): 
        return True
    else:
        return False

def create_download_folder(folder_path):
    if not folder_exists(folder_path):
        os.mkdir(folder_path)

def path_exists(file_name):
    if os.path.exists(file_name):
        return True
    else:
        send_data_string(connection, adderess, '510')
        print('*** Error: the file does not existe')
        return False

def is_file(file_name):
    if os.path.isfile(file_name):
        return True
    else:
        send_data_string(connection, adderess, '510')
        print('*** Error: the path entered does not belong to a file')
        return False

def has_read_permission(file_name):
    if os.access(file_name, os.R_OK):
        return True
    else:
        send_data_string(connection, adderess, '520')
        print('*** Error:', file_name,'file does not have permission to read')
        return False

def is_valid_initial_position(file_initial_position, file_length):
    if (file_initial_position >= file_length) or (file_initial_position < 0):
        send_data_string(connection, adderess, '410')
        print('*** Error: invalid initial position')
        return False
    else:
        return True

def validate_file_maximum_number_bytes(file_initial_position, file_maximum_number_bytes, file_length):
    file_valid_bytes = file_length - file_initial_position
    if (file_maximum_number_bytes == 0) or (file_maximum_number_bytes > file_length) or (file_maximum_number_bytes > file_valid_bytes):
        file_maximum_number_bytes = file_valid_bytes
    return file_maximum_number_bytes
    
def read_file(file_name, file_initial_position, file_maximum_number_bytes):
    try:
        print('*** File found')
        all_data = b''
        
        with open(file_name, 'rb') as file:
            file.seek(file_initial_position) #sets the position of the file where the reading should start
            while file_maximum_number_bytes > 0:
                data = file.read(4096) #read the first 4096 bytes of the file
                all_data += data #saves the respective read data in the all_data variable
                file_maximum_number_bytes -= len(data) 
                
        return all_data
    except:
        send_data_string(connection, adderess, '530')
        print('*** Error reading file')

def open_client_connect(server, port):
    sock =  socket.socket(socket.AF_INET, socket.SOCK_STREAM) #open a tcp connection
    sock.bind((server, port)) #set the correct data for connection
    sock.listen(1) #set the server in passive mode to wait for 1 client request
    print('*** Starting connection with server')
    return sock

def close_client_connect(sock):
    sock.close()
    print('*** Closing connection to server\n\n')

def open_accept_client_connection():
    connection, adderess = sock.accept() #client connection request is accepted
    print('*** Connection accepted\n\n')
    return connection, adderess

def close_accepted_client_connection(connection):
    connection.close()
    print('*** Close connection accepted\n\n')

def client_connection_is_open(flag):
    if flag != '450':
        return True
    else:
        print('*** Error', flag)
        return False

def receive_unpacked_data(struct_type, connection, byte_length):
    data = struct.unpack(struct_type , connection.recv(byte_length))[0]
    print('***', data, 'received')
    return data

def receive_data_string(connection, byte_length):
    data = connection.recv(byte_length).decode('utf-8')
    print('***', data, 'received')
    return data

def send_packaged_data(struct_type, connection, adderess, data):
    data = struct.pack(struct_type, data)
    connection.sendall(data)
    print('*** data sent to', adderess)

def send_data_string(connection, adderess, data):
    connection.sendall(data.encode('utf-8'))
    print('*** data sent to', adderess)

def send_data_byte(connection, adderess, data):
    connection.sendall(data)
    print('*** data sent to', adderess)
    
def main(connection, adderess):
    #receives data about the file to be downloaded from the client
    print('*** Waiting for data')
    file_name_length = receive_unpacked_data('h', connection, 2)
    file_name = receive_data_string(connection, file_name_length)
    
    if client_connection_is_open(file_name):
        file_initial_position = receive_unpacked_data('q', connection, 8)
        file_maximum_number_bytes = receive_unpacked_data('q', connection, 8)

        file_name = os.path.realpath(CURRENT_DIRECTORY_PATH+'/'+FOLDER_PATH+'/'+file_name)

        if path_exists(file_name):
            if is_file(file_name):
                if has_read_permission(file_name):

                    file_length = os.path.getsize(file_name)
                    
                    if is_valid_initial_position(file_initial_position, file_length):
                        file_maximum_number_bytes = validate_file_maximum_number_bytes(file_initial_position, file_maximum_number_bytes, file_length)
                        all_data = read_file(file_name, file_initial_position, file_maximum_number_bytes)

                        send_data_string(connection, adderess, '0') #sends a success flag to the client
                        send_packaged_data('q', connection, adderess, len(all_data)) #sends the size of the transferred file to the client
                        send_data_byte(connection, adderess, all_data) #send the required file to the client
                        print('*** File transferred')
                    
    close_accepted_client_connection(connection)
    
CURRENT_DIRECTORY_PATH = os.path.realpath(os.path.dirname(__file__))
SERVER = '127.0.0.1'
PORT = 12345
FOLDER_PATH = 'Downloads'

create_download_folder(FOLDER_PATH)
sock = open_client_connect(SERVER, PORT)

while True:
    connection, adderess = open_accept_client_connection()
    
    try:
        thread = threading.Thread(target=main, args=(connection, adderess))
        thread.start()
    except:
        print('*** It was not possible to make a new connection')
        
close_client_connect(sock)
