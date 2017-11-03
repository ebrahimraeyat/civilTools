# -*- coding: utf-8 -*-
import csv
import codecs
CODEC = "UTF-8"


def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]


def loadFile(fname):
    fh = codecs.open(unicode("Rus.py"), "w", CODEC)
    fh.write("# -*- coding: utf-8 -*-\nRu = {")
    with open(unicode(fname), 'rb') as stream:
        for rowdata in unicode_csv_reader(stream):
            if rowdata[0] == 'comment':
                continue
            if rowdata[0] == 'title':
                fh.write('},\nu"%s":{' % rowdata[1])
                continue
            else:
                fh.write('u"%s":[%s,%s,%s,%s,%s,%s,%s,%s],\n' % (
                                               rowdata[0],
                                               rowdata[1],
                                               rowdata[2],
                                               rowdata[3],
                                               rowdata[4],
                                               rowdata[5],
                                               rowdata[6],
                                               rowdata[7],
                                               rowdata[8]))
        fh.write("}}")
        fh.close()

loadFile("Ru.csv")

