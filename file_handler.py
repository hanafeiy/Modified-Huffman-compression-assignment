def read_file(filename):
    with open(filename, "rb") as file:
        return file.read()


def write_file(filename, data):
    with open(filename, "wb") as file:
        file.write(data)
