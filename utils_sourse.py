import csv
import time

def to_small_case(text):
    return text.translate(str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)}))

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def write_csv(file, save_dict):
    save_row = {}

    with open(file,'w', encoding='UTF-8') as f:
        writer = csv.DictWriter(f, fieldnames=save_dict[0].keys(),delimiter=",",quotechar='"')
        writer.writeheader()

        k1 = list(save_dict[0].keys())
        length = len(save_dict)

        for i in range(length):
            for k, vs in save_dict[i].items():
                save_row[k] = vs

            writer.writerow(save_row)

def sleep():
    #time.sleep(4 + random.randint(1, 2))
    time.sleep(3)

def short_sleep():
    #time.sleep(2 + random.randint(1, 2))
    time.sleep(1)