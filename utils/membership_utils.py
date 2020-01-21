from utils.log_manager import log_manager
from utils.general_utils import delete_collection

logger = log_manager("membership_utils")


def create_sub_collection_member(client, id, collection_name, document_name, document_value):
    """
    :param id:
    :param collection_name:
    :param document_name:
    :param document_value:
    :return: -1 if failed
    """
    try:
        docs = client.collection(u'members').document(id).collection(collection_name)
        docs.document(document_name).set(document_value)
    except Exception as e:
        logger.error("Cannot create sub collection " + str(e))
        print('Cannot create sub collection')
        return -1


def get_attribute_from_member(client, studentid, attr_name):
    """
    get an attribute value from a member, if exist. If not, return -1
    :param client:
    :param studentid:
    :param attr_name:
    :return: -1 if attribute does not exist
    """
    try:
        info = client.collection(u'members').document(studentid).get()
        value = info.to_dict()[attr_name]
        return value
    except Exception as e:
        logger.error("Cannot get value from the attribute! " + str(e))
        print("Cannot get value from attribute!")
        return -1


def change_attribute_of_member(client, studentid, attr_name, attr_value):
    """
    change an attribute value to an attribute under a member
    :param client: firestore client object
    :param studentid: membership number to identify the member in firestore
    :param attr_name:
    :param attr_value:
    :return:
    """
    try:
        client.collection(u'members').document(studentid).update({
            attr_name: attr_value
        })
    except Exception as e:
        logger.error("Cannot update attribute value to attribute! " + str(e))
        print("Cannot update attribute value to attribute! ")
        return -1


def attibutes_to_list(client, attribute_name):
    """
    output a list of attribute values in firestore
    :param client: firestore client object
    :param attribute_name: the name of attribute stored as key in firestore entry
    :return:
    """
    output = list()
    try:
        members = client.collection(u'members').get()
    except Exception as e:
        logger.error("Cannot get documents from collection - Firestore. " + str(e))
        print("Failed to get document from collection! ")
        return None
    for member in members:
        try:
            value = member.get(attribute_name)
        except Exception as e:
            logger.error("Cannot get attribute values from document. " + str(e))
            print("Failed to get attribute from document! ")
            return None
        output.append(value)
    return output


def create_members_dictionary(client):
    final = list()
    try:
        docs = client.collection(u'members').get()
        for doc in docs:
            final.append(doc.to_dict())
        return final
    except Exception as e:
        logger.error("Cannot create members dictionary " + str(e))
        print('Cannot create members dictionary')


def get_loaning_status(client, id):
    output = list()
    try:
        docs = client.collection(u'members').document(id).collection('loaned_items').get()
        for item in docs:
            output.append(item.to_dict())
        return output
    except Exception as e:
        logger.error("Cannot get members loaning info " + str(e))
        print('Cannot get members loaning info')


def check_sub_doc_exist_x(client, student_id, item_id):
    try:
        exists = client.collection(u'members').document(student_id).collection('loaned_items').document(item_id).get().exists
        if exists:
            return True
        else:
            return False
    except Exception as e:
        logger.error("Cannot connect to Firestore " + str(e))
        print('Cannot connect to Firestore', e)
        return -1


def get_attr_from_sub_doc_x(client, student_id, item_id, attr_name):
    try:
        loaner = client.collection(u'members').document(student_id).collection('loaned_items').document(item_id).get()
        infos = loaner.to_dict()
        value = infos[attr_name]
        return value
    except Exception as e:
        print("attr name not exist!", e)
        return -1


def delete_sub_coll_x(client, student_id):
    try:
        collection = client.collection(u'members').document(student_id).collection('loaned_items')
        delete_collection(collection, 5)
        return True
    except Exception as e:
        print("Cannot delete member loaned items!", e)
        return -1


def delete_sub_coll_doc(client, student_id, item_id):
    try:
        client.collection(u'members').document(student_id).collection('loaned_items').document(item_id).delete()
        return True
    except Exception as e:
        print("Cannot delete the loaned item from member's record!", e)
        return -1


def get_attributes_from_sub_coll(client, student_id, attr_name):
    output = list()
    try:
        docs = client.collection(u'members').document(student_id).collection(u'loaned_items').get()
        for doc in docs:
            value = doc.to_dict()[attr_name]
            output.append(value)
        return output
    except Exception as e:
        print("Cannot get attributes from sub collection!", e)
        return -1


def update_sub_coll_attribute(client, student_id, item_id, attr_name, update_value):
    try:
        client.collection(u'members').document(student_id).collection(u'loaned_items').document(item_id).update({
            attr_name: update_value
        })
    except Exception as e:
        print("Cannot update attributes from sub collection!", e)
        return -1
