import csv

class CSVManager:
    def __init__(self, file_path):
        self.file_path = file_path

    def read_csv(self, skip_header=False):
        with open(self.file_path, mode='r', newline='') as file:
            reader = csv.reader(file)
            if skip_header:
                next(reader, None)
            data = [row for row in reader]
        return data

    def write_csv(self, data):
        with open(self.file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)