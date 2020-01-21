from flask import Blueprint, redirect, url_for, render_template, flash, request
from utils.auth import is_admin
from utils.general_utils import generate_id, decode_id
from utils.intentory_utils import (create_inventory_dictionary,
                                   inventory_attr_to_list,
                                   create_new_entry,
                                   update_attribute_value,
                                   get_loaners,
                                   get_attribute_value,
                                   delete_sub_doc,
                                   get_sub_attr_from_member,
                                   update_attr_sub_coll)
from utils.membership_utils import (create_members_dictionary,
                                    change_attribute_of_member,
                                    get_attribute_from_member,
                                    get_loaning_status,
                                    delete_sub_coll_x,
                                    get_attributes_from_sub_coll,
                                    update_sub_coll_attribute,
                                    get_attr_from_sub_doc_x,
                                    delete_sub_coll_doc)
from utils.email import send_email
from firebase import fs
import datetime

admin_api = Blueprint("admin_api", __name__)
client = fs.get_client()


@admin_api.route('/admin')
@admin_api.route('/admin/index')
def index():
    if is_admin():
        return render_template('index.html')
    else:
        flash("You are unauthorized!")
        return redirect(url_for('login_api.login'))


@admin_api.route('/admin/inventory', methods=['GET','POST'])
def inventory():
    inventory = create_inventory_dictionary()
    if is_admin():
        if request.method == 'POST':
            try:
                selection = request.form['inventory-option']
            except:
                selection = None

            if selection == 'add':
                try:
                    name = request.form['inventory-name']
                except:
                    flash("Fields empty! Unable to add new entry.", 'warn')
                    return render_template('inventory.html', inventory=inventory)
                try:
                    quantity = request.form['inventory-quantity']
                    if isinstance(quantity, float):
                        flash("Quantity must be an integer!",'warn')
                        return render_template('inventory.html', inventory=inventory)
                    if quantity == "":
                        flash("Fields empty! Unable to add new entry.", 'warn')
                        return render_template('inventory.html', inventory=inventory)
                except:
                    flash("Fields empty! Unable to add new entry.", 'warn')
                    return render_template('inventory.html', inventory=inventory)
                try:
                    type = request.form['inventory-type']
                    if type == "":
                        flash("Fields empty! Unable to add new entry.", 'warn')
                        return render_template('inventory.html', inventory=inventory)
                except:
                    flash("Fields empty! Unable to add new entry.", 'warn')
                    return render_template('inventory.html', inventory=inventory)

                try:
                    info = request.form['info']
                except:
                    info = ""

                try:
                    loanable = request.form['inventory-loanable']
                    loanable = True if loanable == "on" else False
                except:
                    loanable = False

                last_id = decode_id(inventory_attr_to_list("id")[-1])
                next_id = generate_id(last_id+1)

                new_entry = {
                    'id': next_id,
                    'name': name,
                    'type': type,
                    'quantity': quantity,
                    'info': info,
                    'is_allow': loanable
                }

                try:
                    create_new_entry(next_id, new_entry)
                except Exception as e:
                    flash("Failed to create new entry! {}".format(e))
                    return redirect(url_for('error_api.error'))

                flash("New entry successfully created. ID: {}".format(next_id), 'success')
                inventory = create_inventory_dictionary()
                return render_template('inventory.html', inventory=inventory)

            elif selection == 'update':
                try:
                    _id = request.form['update-selection']
                    if _id == "":
                        flash("Fields empty! Unable to add new entry.", 'warn')
                        return render_template('inventory.html', inventory=inventory)
                except:
                    flash("Please select an item first in order to update! ", 'warn')
                    return render_template('inventory.html', inventory=inventory)
                try:
                    quantity = request.form['update-quantity']
                    if isinstance(quantity, float):
                        flash("Quantity must be an integer!",'warn')
                        return render_template('inventory.html', inventory=inventory)
                    if quantity == "":
                        quantity = "unchanged"
                except:
                    quantity = "unchanged"
                try:
                    info = request.form['info2']
                    if info == "":
                        info = "unchanged"
                except:
                    info = "unchanged"
                try:
                    loanable = request.form['update-loanable']
                    loanable = True if loanable == "on" else False
                except:
                    loanable = False

                if info != "unchanged":
                    status = update_attribute_value(_id, 'info', info)
                    if status == -1:
                        return render_template('inventory.html', inventory=inventory)

                if quantity != 'unchanged':
                    status = update_attribute_value(_id, 'quantity', int(quantity))
                    if status == -1:
                        return render_template('inventory.html', inventory=inventory)
                if loanable != 'unchanged':
                    status = update_attribute_value(_id, 'is_allow', loanable)
                    if status == -1:
                        return render_template('inventory.html', inventory=inventory)

                flash("Item successfully updated. ID: {}".format(_id), 'success')
                inventory = create_inventory_dictionary()
                return render_template('inventory.html', inventory=inventory)

            elif selection == "view":
                try:
                    _id = request.form['view-inventory']
                    if _id == "":
                        flash("Fields empty! Unable to add new entry.", 'warn')
                        return render_template('inventory.html', inventory=inventory)
                except:
                    flash("Please select an item first in order to update! ", 'warn')
                    return render_template('inventory.html', inventory=inventory)

                return redirect(url_for('admin_api.inventory_info', item_id=_id))

            else:
                flash("Invalid selection!", 'warn')
                return render_template('inventory.html', inventory=inventory)
        else:
            return render_template('inventory.html', inventory=inventory)
    else:
        flash("You are unauthorized!")
        return redirect(url_for('login_api.login'))


@admin_api.route('/admin/inventory/<item_id>', methods=['GET', 'POST'])
def inventory_info(item_id):
    if is_admin():
        loaners = get_loaners(item_id)
        name = get_attribute_value(item_id, 'name')
        if len(loaners) == 0:
            flash("There is no loaner's record under this item", 'warn')
            return render_template('inventory_info.html', loaners=loaners, item_id=item_id, name=name)
        for loaner in loaners:
            has_expired = False
            expiry = loaner['expiry']
            now = datetime.datetime.now()
            if datetime.datetime.timestamp(now) > datetime.datetime.timestamp(expiry):
                has_expired = True
            loaner['expired_status'] = has_expired

        if request.method == "POST":
            try:
                remind_btn = request.form['remind']
            except:
                remind_btn = None

            try:
                return_one = request.form['return_one']
            except:
                return_one = None

            try:
                return_all = request.form['return_all']
            except:
                return_all = None

            if remind_btn is not None:
                student_id = remind_btn
                expired_items_str = ""
                student_email = get_attribute_from_member(client, student_id, "email")
                loaned_items = get_loaning_status(client, student_id)
                now = datetime.datetime.now()
                for item in loaned_items:
                    expiry = item['expiry']
                    if datetime.datetime.timestamp(now) > datetime.datetime.timestamp(expiry):
                        expired_items_str += "Item: {} , Item ID: {} , Expiry Date: {}\n".format(item['name'],
                                                                                                 item['id'], expiry)

                reminder_email = '''
                Dear {},

                You have expired item(s) that have yet to be returned!
                Please return them ASAP otherwise you will not be able to loan any more item.

                Your expire item is/are:

                {}

                Please make an arrangement with any of the exco members via Telegram or Email to return your item.

                Thank you for your understanding!

                IEEE SUTD Student Branch
                IEEE Web Development Team

                [This is an auto-generated email. Please do not reply.]
                '''.format(name, expired_items_str)
                send_email(reminder_email.encode('utf-8'), student_email)
                flash("Reminder email has been successfully sent to {}".format(name), 'success')
                return render_template('inventory_info.html', loaners=loaners, item_id=item_id, name=name)

            elif return_one is not None:
                student_id = return_one
                old_quantity = get_attr_from_sub_doc_x(client, student_id, item_id, "quantity")
                new_quantity = old_quantity - 1
                old_limit = get_attribute_from_member(client, student_id, "limit")
                if new_quantity == 0:
                    a = delete_sub_doc(item_id, student_id)
                    b = delete_sub_coll_doc(client, student_id, item_id)
                    if a == -1 or b == -1:
                        flash("Unable to update sub collection loaned item quantity!")
                        return redirect(url_for('error_api.error'))
                else:
                    old_quantity_from_inventory = get_sub_attr_from_member(item_id, student_id, "quantity")
                    new_quantity_from_inventory = old_quantity_from_inventory - 1
                    status = update_sub_coll_attribute(client, student_id, item_id, "quantity", new_quantity)
                    status_inventory = update_attr_sub_coll(item_id, student_id, "quantity",
                                                            new_quantity_from_inventory)
                    if status == -1 or status_inventory == -1:
                        flash("Unable to update sub collection loaned item quantity!")
                        return redirect(url_for('error_api.error'))
                new_limit = old_limit + 1
                limit_update = change_attribute_of_member(client, student_id, "limit", new_limit)
                if limit_update == -1:
                    flash("Failed to update member's limit.")
                    return redirect(url_for('error_api.error'))
                old_quantity_inventory = get_attribute_value(item_id, "quantity")
                new_quantity_inventory = old_quantity_inventory + 1
                status_update = update_attribute_value(item_id, "quantity", new_quantity_inventory)
                if status_update == -1:
                    flash("Failed to update quantity in the main inventory system.")
                    return redirect(url_for('error_api.error'))
                loaners = get_loaners(item_id)
                if len(loaners) == 0:
                    flash("There is no loaner's record under this item", 'warn')
                    return render_template('inventory_info.html', loaners=loaners, item_id=item_id, name=name)
                for loaner in loaners:
                    has_expired = False
                    expiry = loaner['expiry']
                    now = datetime.datetime.now()
                    if datetime.datetime.timestamp(now) > datetime.datetime.timestamp(expiry):
                        has_expired = True
                    loaner['expired_status'] = has_expired
                return render_template('inventory_info.html', loaners=loaners, item_id=item_id, name=name)

            elif return_all is not None:
                student_id = return_all
                old_limit = get_attribute_from_member(client, student_id, "limit")
                old_loaned_quantity = get_attr_from_sub_doc_x(client, student_id, item_id, "quantity")
                old_quantity_inventory = get_attribute_value(item_id, "quantity")
                new_quantity_inventory = old_quantity_inventory + old_loaned_quantity
                new_limit = old_limit + old_loaned_quantity
                limit_update = change_attribute_of_member(client, student_id, "limit", new_limit)
                if limit_update == -1:
                    flash("Failed to update member's limit.")
                    return redirect(url_for('error_api.error'))
                status_update = update_attribute_value(item_id, "quantity", new_quantity_inventory)
                status_delete = delete_sub_coll_doc(client, student_id, item_id)
                status_delete_inventory = delete_sub_doc(item_id, student_id)
                if status_update == -1 or status_delete == -1 or status_delete_inventory == -1:
                    flash("Failed to update quantity in the main inventory system.")
                    return redirect(url_for('error_api.error'))
                loaners = get_loaners(item_id)
                if len(loaners) == 0:
                    flash("There is no loaner's record under this item", 'warn')
                    return render_template('inventory_info.html', loaners=loaners, item_id=item_id, name=name)
                for loaner in loaners:
                    has_expired = False
                    expiry = loaner['expiry']
                    now = datetime.datetime.now()
                    if datetime.datetime.timestamp(now) > datetime.datetime.timestamp(expiry):
                        has_expired = True
                    loaner['expired_status'] = has_expired
                return render_template('inventory_info.html', loaners=loaners, item_id=item_id, name=name)
        else:
            return render_template('inventory_info.html', loaners=loaners, item_id=item_id, name=name)
    else:
        flash("You are unauthorized!")
        return redirect(url_for('login_api.login'))


@admin_api.route('/admin/members', methods=['GET', 'POST'])
def members():
    if is_admin():
        member_list = create_members_dictionary(client)
        length = len(member_list)
        if member_list is None:
            flash("Failed to extract member information from Firebase!")
            return redirect(url_for('error_api.error'))
        if request.method == "POST":
            stdid = request.form['reset']
            stdname = get_attribute_from_member(client, stdid, 'name')
            if stdname == -1:
                flash("Unable to get member's name. Check log for more details. Source: get_attribute_from_member")
                return redirect(url_for('error_api.error'))
            change_attribute_of_member(client, stdid, "limit", 5)
            loaned_items = get_attributes_from_sub_coll(client, stdid, "id")
            x = delete_sub_coll_x(client, stdid)
            if x == -1:
                flash("Unable to delete sub collection from user {}".format(stdid))
                return redirect(url_for('error_api.error'))
            if not loaned_items == -1:
                for item_id in loaned_items:
                    y = delete_sub_doc(item_id, stdid)
                    if y == -1:
                        flash("Unable to delete {}'s record in item {}".format(stdid, item_id))
                        return redirect(url_for('error_api.error'))
            flash("Member {} {}'s limit has been reset!".format(stdid, stdname), 'success')
            member_list = create_members_dictionary(client)
            length = len(member_list)
            return render_template('members.html', members=member_list, length=length)
        else:
            return render_template('members.html', members=member_list, length=length)
    else:
        flash("You are unauthorized!")
        return redirect(url_for('login_api.login'))


@admin_api.route('/admin/members/<student_id>', methods=['GET', 'POST'])
def member_info(student_id):
    if is_admin():
        info = get_loaning_status(client, student_id)
        name = get_attribute_from_member(client, student_id, 'name')

        has_expired = False
        expiry_dates = get_attributes_from_sub_coll(client, student_id, "expiry")
        now = datetime.datetime.now()

        for date in expiry_dates:
            if datetime.datetime.timestamp(now) > datetime.datetime.timestamp(date):
                has_expired = True
                break

        if request.method == "POST":

            try:
                remind_btn = request.form['remind']
            except:
                remind_btn = None

            try:
                return_one = request.form['return_one']
            except:
                return_one = None

            try:
                return_all = request.form['return_all']
            except:
                return_all = None

            if remind_btn is not None:

                expired_items_str = ""
                student_email = get_attribute_from_member(client, student_id, "email")
                loaned_items = get_loaning_status(client, student_id)
                now = datetime.datetime.now()
                for item in loaned_items:
                    expiry = item['expiry']
                    if datetime.datetime.timestamp(now) > datetime.datetime.timestamp(expiry):
                        expired_items_str += "Item: {} , Item ID: {} , Expiry Date: {}\n".format(item['name'], item['id'], expiry)

                reminder_email = '''
                Dear {},
                
                You have expired item(s) that have yet to be returned!
                Please return them ASAP otherwise you will not be able to loan any more item.
                
                Your expire item is/are:
                
                {}
                
                Please make an arrangement with any of the exco members via Telegram or Email to return your item.
                
                Thank you for your understanding!
                
                IEEE SUTD Student Branch
                IEEE Web Development Team
                
                [This is an auto-generated email. Please do not reply.]
                '''.format(name, expired_items_str)
                send_email(reminder_email.encode('utf-8'), student_email)
                flash("Reminder email has been successfully sent to {}".format(name), 'success')
                return render_template('member_info.html', info=info, name=name, expired=has_expired)

            elif return_one is not None:
                item_id = return_one
                old_quantity = get_attr_from_sub_doc_x(client, student_id, item_id, "quantity")
                new_quantity = old_quantity - 1
                old_limit = get_attribute_from_member(client, student_id, "limit")
                if new_quantity == 0:
                    a = delete_sub_doc(item_id, student_id)
                    b = delete_sub_coll_doc(client, student_id, item_id)
                    if a == -1 or b == -1:
                        flash("Unable to update sub collection loaned item quantity!")
                        return redirect(url_for('error_api.error'))
                else:
                    old_quantity_from_inventory = get_sub_attr_from_member(item_id, student_id, "quantity")
                    new_quantity_from_inventory = old_quantity_from_inventory - 1
                    status = update_sub_coll_attribute(client, student_id, item_id, "quantity", new_quantity)
                    status_inventory = update_attr_sub_coll(item_id, student_id, "quantity", new_quantity_from_inventory)
                    if status == -1 or status_inventory == -1:
                        flash("Unable to update sub collection loaned item quantity!")
                        return redirect(url_for('error_api.error'))
                new_limit = old_limit + 1
                limit_update = change_attribute_of_member(client, student_id, "limit", new_limit)
                if limit_update == -1:
                    flash("Failed to update member's limit.")
                    return redirect(url_for('error_api.error'))
                old_quantity_inventory = get_attribute_value(item_id, "quantity")
                new_quantity_inventory = old_quantity_inventory + 1
                status_update = update_attribute_value(item_id, "quantity", new_quantity_inventory)
                if status_update == -1:
                    flash("Failed to update quantity in the main inventory system.")
                    return redirect(url_for('error_api.error'))
                info = get_loaning_status(client, student_id)
                return render_template('member_info.html', info=info, name=name, expired=has_expired)

            elif return_all is not None:
                item_id = return_all
                old_limit = get_attribute_from_member(client, student_id, "limit")
                old_loaned_quantity = get_attr_from_sub_doc_x(client, student_id, item_id, "quantity")
                old_quantity_inventory = get_attribute_value(item_id, "quantity")
                new_quantity_inventory = old_quantity_inventory + old_loaned_quantity
                new_limit = old_limit + old_loaned_quantity
                limit_update = change_attribute_of_member(client, student_id, "limit", new_limit)
                if limit_update == -1:
                    flash("Failed to update member's limit.")
                    return redirect(url_for('error_api.error'))
                status_update = update_attribute_value(item_id, "quantity", new_quantity_inventory)
                status_delete = delete_sub_coll_doc(client, student_id, item_id)
                status_delete_inventory = delete_sub_doc(item_id, student_id)
                if status_update == -1 or status_delete == -1 or status_delete_inventory == -1:
                    flash("Failed to update quantity in the main inventory system.")
                    return redirect(url_for('error_api.error'))
                info = get_loaning_status(client, student_id)
                return render_template('member_info.html', info=info, name=name, expired=has_expired)
        else:
            return render_template('member_info.html', info=info, name=name, expired=has_expired)

    else:
        flash("You are unauthorized!")
        return redirect(url_for('login_api.login'))
