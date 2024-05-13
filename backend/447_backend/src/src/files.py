def read_file(file_path):
    file = open(file_path)
    content = file.read()
    file.close()
    return content


# concatenates file directory with file name, returns file contents as a string
def read_file_in(file_directory, file_name): 
    return read_file(f"{file_directory}\\{file_name}")