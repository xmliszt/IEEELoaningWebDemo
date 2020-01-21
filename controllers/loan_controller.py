from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from utils.auth import is_login, is_admin
from utils.intentory_utils import create_inventory_dictionary, get_attribute_value, update_attribute_value, create_sub_collection, check_sub_doc_exist, get_sub_attr_from_member
from utils.membership_utils import get_attribute_from_member, change_attribute_of_member, create_sub_collection_member, get_loaning_status, get_attr_from_sub_doc_x, check_sub_doc_exist_x, get_attributes_from_sub_coll
from utils.email import send_email
from firebase import fs
import datetime
from time import sleep

loan_api = Blueprint("loan_api", __name__)
client = fs.get_client()


@loan_api.route('/', methods=['POST', 'GET'])
@loan_api.route('/loan', methods=['POST', 'GET'])
def loan():
    logged_in = is_login()
    admin = is_admin()
    if logged_in:
        inventory = create_inventory_dictionary()
        session_name = session['name']
        student_id = session['id']

        if request.method == "POST":
            try:
                picked_id = request.form['select']
            except Exception as e:
                print("No selection is done!", e)
                flash("You have yet to select anything!")
                return render_template('loan.html', name=session_name, inventory=inventory, id=student_id, admin=admin)

            quantity = get_attribute_value(picked_id, "quantity")
            item_name = get_attribute_value(picked_id, "name")
            limits = get_attribute_from_member(client, student_id, "limit")
            expiry_dates = get_attributes_from_sub_coll(client, student_id, "expiry")
            now = datetime.datetime.now()

            for date in expiry_dates:
                if datetime.datetime.timestamp(now) > datetime.datetime.timestamp(date):
                    flash("You have expired item(s). Please check your loan record and return the expired item before making a new loan!")
                    return redirect(url_for('confirm_api.confirm'))

            if limits == 0:
                flash("You have already loaned 5 items! You can't loan until you return them.")
                return redirect(url_for('confirm_api.confirm'))

            if quantity == 0:
                flash("You selected an item which is run out. Please select other items we have.")
                return redirect(url_for('confirm_api.confirm'))

            update_attribute_value(picked_id, "quantity", quantity-1)
            change_attribute_of_member(client, student_id, "limit", limits-1)

            # for inventory side
            is_exist = check_sub_doc_exist(picked_id, student_id)
            if is_exist:
                number = get_sub_attr_from_member(picked_id, student_id, "quantity")
                if number == -1:
                    number = 0
            else:
                number = 0

            # for member side
            x_is_exist = check_sub_doc_exist_x(client, student_id, picked_id)
            if x_is_exist:
                x_number = get_attr_from_sub_doc_x(client, student_id, picked_id, "quantity")
                if x_number == -1:
                    x_number = 0
            else:
                x_number = 0

            expiry = now + datetime.timedelta(days=30)

            student_email = get_attribute_from_member(client, student_id, "email")
            std_name = get_attribute_from_member(client, student_id, "name")

            sub_object = {
                "student": student_id,
                "name": std_name,
                "email": student_email,
                "quantity": number+1,
                "expiry": expiry
            }
            sub_object_2 = {
                "id": picked_id,
                "name": item_name,
                "quantity": x_number+1,
                "expiry": expiry
            }
            inventory_updated = create_sub_collection(picked_id, "loaners", student_id, sub_object)
            member_updated = create_sub_collection_member(client, student_id, "loaned_items", picked_id, sub_object_2)

            if inventory_updated == -1 or member_updated == -1:
                flash("Can't create sub collection!")
                return redirect(url_for('error_api.error'))

            new_quantity = get_attribute_value(picked_id, "quantity")
            new_limit = get_attribute_from_member(client, student_id, "limit")

            student_name = get_attribute_from_member(client, student_id, "name")
            student_email = get_attribute_from_member(client, student_id, "email")

            master_email = '''
            [Inventory System Update]
            --Item: {}
            --Item ID: {}
            --Quantity left: {}
            
            was loaned out successfully
            by
            
            --Student ID: {}
            --Studnet name: {}
            --Remaining loans: {}
            
            Item expiry date is set to be:
            {}
            '''.format(item_name, picked_id, new_quantity, student_id, student_name, new_limit, datetime.datetime.strftime(now, "%Y-%m-%d %H:%M:%S"))

            loaner_email = '''
            Thank you for using IEEE SUTD Student Branch online inventory loaning system.
            Here is a summary for your loaning status.
            
            --Loaned Item: {}
            --Item ID: {}
            --Expiry date: {}
            
            Please make an arrangement with any of the exco members via Telegram or Email to collect your item.
            
            For further query, please contact us at ieee@club.sutd.edu.sg
            Please remember to return your item before the expiry date.
            Thank you for your understanding!
            
            IEEE SUTD Student Branch
            IEEE Web Development Team
            
            [This is an auto-generated email. Please do not reply.]
            '''.format(item_name, picked_id, datetime.datetime.strftime(now, "%Y-%m-%d %H:%M:%S"))

            send_email(master_email.encode('utf-8'), "ieee@club.sutd.edu.sg")
            sleep(1)
            send_email(loaner_email.encode('utf-8'), student_email)

            flash_message = "You picked {}. " \
                            "Now left {}. " \
                            "Remaining number of items you can loan: {}. " \
                            "Check your loaned item here".format(item_name, new_quantity, new_limit)
            flash(flash_message)
            return redirect(url_for('confirm_api.confirm'))
        else:
            return render_template('loan.html', name=session_name, inventory=inventory, id=student_id, admin=admin)
    else:
        flash("Please login first!")
        return redirect(url_for('login_api.login'))


@loan_api.route('/loan/<student_id>')
def loan_info(student_id):
    logged_in = is_login()
    if logged_in:
        if session['id'] == student_id:
            is_self = True
        else:
            is_self = False
        if is_self:
            has_expired = False
            expiry_dates = get_attributes_from_sub_coll(client, student_id, "expiry")
            now = datetime.datetime.now()

            for date in expiry_dates:
                if datetime.datetime.timestamp(now) > datetime.datetime.timestamp(date):
                    has_expired = True
                    break

            info = get_loaning_status(client, student_id)
            name = get_attribute_from_member(client, student_id, 'name')
            return render_template('loan_info.html', info=info, name=name, expired=has_expired)
        else:
            flash("You are trying to view other people's loan information. Please sign in your own account and try again!")
            return redirect(url_for('login_api.login'))
    else:
        flash("Please login first!")
        return redirect(url_for('login_api.login'))
