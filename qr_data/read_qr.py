import csv


def obtain_qr_from_file(filename='qr_data.csv', nrow=1, _delimiter=','):
    with open(filename) as csv_file:

        csv_reader = csv.reader(csv_file, delimiter=_delimiter)
        line_count = 0

        for row in csv_reader:

            if line_count == 0:

                #print(f'Column names are {", ".join(row)}')
                line_count += 1

            else:

                if line_count == nrow:
                    return row[1:]
                line_count += 1
