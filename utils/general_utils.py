import os
import csv
from utils.log_manager import log_manager


logger = log_manager("general_utils")


def make_directory(path):
    """
    create directory if not exist, check otherwise
    :param path:
    :return: True if exist | False if not exist
    """
    if not os.path.exists(path):
        os.mkdir(path)
        return False
    else:
        return True


def decode_id(id):
    """
    decode string id to integer
    :param id:
    :return:
    """
    number = id.lstrip('0')
    try:
        output = int(number)
        return output
    except Exception as e:
        print("ID is not an integer format.", e)
        logger.error("Failed to convert id to integer. " + str(e))
        return -1


def generate_id(id=0):
    """
    pass integer id to generate a string of id with 0 as placeholder
    :param id: integer
    :return: -1 if failed
    """
    if not isinstance(id, int):
        print("Please enter an integer for id generation")
        return -1
    if id > 999:
        print("id exceed limit 999")
        return -1
    output = "{:0>3d}".format(id)
    return output


def append_csv(path, *args):
    """
    append rows into existing csv file
    :param path: path to target csv
    :param args:
    :return:
    """
    try:
        make_directory("src")
        with open(path, 'a+', encoding='utf-8', newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(args)
            fh.close()
    except Exception as e:
        logger.error(e)
        print("Fail to append. CSV file does not exist! ", e)


def delete_collection(coll_ref, batch_size):
    docs = coll_ref.limit(10).get()
    deleted = 0

    for doc in docs:
        print(u'Deleting doc {} => {}'.format(doc.id, doc.to_dict()))
        doc.reference.delete()
        deleted = deleted + 1

    if deleted >= batch_size:
        return delete_collection(coll_ref, batch_size)
