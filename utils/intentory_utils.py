from firebase import fs
from utils.log_manager import log_manager
from flask import flash
from utils.general_utils import delete_collection

logger = log_manager("inventory_utils")
client = fs.get_client()


def inventory_attr_to_list(attr_name):
    """
    :param attr_name:
    :return:
    """
    output = list()
    try:
        items = client.collection(u'inventory').get()
    except Exception as e:
        logger.error("Cannot get documents from inventory - Firestore. " + str(e))
        print("Failed to get document from inventory! ")
        return None
    for item in items:
        try:
            value = item.get(attr_name)
        except Exception as e:
            logger.error("Cannot get attribute values from document. " + str(e))
            print("Failed to get attribute from document! ")
            return None
        output.append(value)
    return output


def create_sub_collection(id, collection_name, document_name, document_value):
    """
    :param id:
    :param collection_name:
    :param document_name:
    :param document_value:
    :return: -1 if failed
    """
    try:
        docs = client.collection(u'inventory').document(id).collection(collection_name)
        docs.document(document_name).set(document_value)
    except Exception as e:
        logger.error("Cannot create sub collection " + str(e))
        print('Cannot create sub collection')
        return -1


def create_inventory_dictionary():
    """
    :return:
    """
    final = list()
    try:
        docs = client.collection(u'inventory').get()
        for doc in docs:
            final.append(doc.to_dict())
        return final
    except Exception as e:
        logger.error("Cannot create inventory dictionary " + str(e))
        print('Cannot create inventory dictionary')


def get_loaners(id):
    output = list()
    try:
        loaners = client.collection(u'inventory').document(id).collection('loaners').get()
        for loaner in loaners:
            output.append(loaner.to_dict())
        return output
    except:
        return None


def get_attribute_value(id, attr_name):
    """
    :param attr_name:
    :return:
    """
    try:
        obj = client.collection(u'inventory').document(id).get()
        value = obj.to_dict()[attr_name]
        return value
    except Exception as e:
        logger.error("Cannot get attribute from inventory " + str(e))
        print('Cannot get attribute from inventory')
        return -1


def update_attribute_value(id, attr_name, new):
    """
    :param id:
    :param attr_name:
    :param new:
    :return:
    """
    try:
        client.collection(u'inventory').document(id).update({
            attr_name: new
        })
    except Exception as e:
        logger.error("Cannot update inventory " + str(e))
        flash("Unable to update inventory attribute values. " + str(e), 'warn')
        return -1

def create_new_entry(id, entry_object):
    """
    :param id:
    :param entry_object:
    :return:
    """
    client.collection(u'inventory').document(id).set(entry_object)


def check_sub_doc_exist(item_id, loaner_id):
    try:
        status = client.collection(u'inventory').document(item_id).collection('loaners').document(loaner_id).get().exists
        if status is True:
            return True
        else:
            return False
    except Exception as e:
        print("Cannot connect to Firestore.", e)
        return -1


def get_sub_attr_from_member(item_id, loaner_id, attr_name):
    try:
        loaner = client.collection(u'inventory').document(item_id).collection('loaners').document(loaner_id).get()
        infos = loaner.to_dict()
        value = infos[attr_name]
        return value
    except Exception as e:
        print("attr name not exist!", e)
        return -1


def delete_sub_doc(item_id, loaner_id):
    try:
        client.collection(u'inventory').document(item_id).collection('loaners').document(loaner_id).delete()
        return True
    except Exception as e:
        print("Cannot delete item individual loaned history!", e)
        return -1


def get_attributes_from_sub_coll_inventory(item_id, attr_name):
    output = list()
    try:
        docs = client.collection(u'inventory').document(item_id).collection('loaners').get()
        for doc in docs:
            value = doc.to_dict()[attr_name]
            output.append(value)
        return output
    except Exception as e:
        print("Cannot get sub attributes from inventory", e)
        return -1


def update_attr_sub_coll(item_id, loaner_id, attr_name, update_value):
    try:
        client.collection(u'inventory').document(item_id).collection('loaners').document(loaner_id).update({
            attr_name: update_value
        })
    except Exception as e:
        print("Cannot update sub-attribute of loaned item !", e)
        return -1
