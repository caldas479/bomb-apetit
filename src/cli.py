from __future__ import print_function, unicode_literals
import json
import connection_interface

from PyInquirer import prompt, Separator
from prompt_toolkit.validation import Validator, ValidationError
from examples import custom_style_2
from security_library.algos import generate_signature, verify_signature, encrypt_with_public_key, check_timestamp, write_key_to_file
from security_library.secure_documents import unprotect_json, check_json


restaurants = []
global who
who = ""

class ReviewValidator(Validator):
    def validate(self, number):
        try:
            int(number.text)
        except ValueError:
            raise ValidationError(
                message='Please enter an integer',
                cursor_position=len(number.text))  # Move cursor to end
        
        if not (1 <= int(number.text) <= 5):
                raise ValidationError(
                message='Please enter an integer between 1 and 5',
                cursor_position=len(number.text))  
       

def list_users():
    users = connection_interface.listUsers()
    if check_timestamp(users["timestamp"]):
        user_list = []
        for user in users["Users"]:
            user_list += [user["User Name"] ,]
        return user_list
    else:
        print("Server response failed freshness. Try Again")

def get_restaurants():
    json_object = connection_interface.vouchers()
    if check_timestamp(json_object["timestamp"]):
        if json_object is not None:
            for obj in json_object["documents"]:
                global restaurants
                if obj["Restaurant Name"] and obj["Restaurant Name"] not in restaurants:
                    restaurants += [obj["Restaurant Name"] ,]
    else:
        print("Server response failed freshness. Try Again")

def get_users_keys():
    json_object = connection_interface.keys()
    if check_timestamp(json_object["timestamp"]):
        if json_object is not None:
            for key in json_object["keys"]:
                write_key_to_file(key["val"],key["path"])

def get_vouchers():
    json_object = connection_interface.vouchers()

    vouchers = []
    if check_timestamp(json_object["timestamp"]):
        if json_object is not None:
            for obj in json_object["documents"]:
                voucher = []
                if obj["Text"] is not None:
                    obj_text = json.loads(obj['Text'])
                    if "restaurantInfo" in obj_text and "mealVoucher" in obj_text["restaurantInfo"]:
                        voucher += [obj["Restaurant Name"] + ":" ,]
                        key = f'keys/users/{who}/private_key.pem'
                        restaurant_pu = connection_interface.requestRestaurantPublicKey(obj["Restaurant Name"])
                        if not check_timestamp(restaurant_pu["timestamp"]):
                            print("Server response failed freshness. Try Again")
                            return
                        if not check_json(obj_text, restaurant_pu["RPK"]):
                            print("Data is not authentic!")
                            return
                        
                        unprotected_data = unprotect_json(obj_text, key)
                        voucher += [unprotected_data["restaurantInfo"]["mealVoucher"]["code"] + ": " + unprotected_data["restaurantInfo"]["mealVoucher"]["description"] ,]

                    vouchers += [voucher ,]
            return vouchers
    else:
        print("Server response failed freshness. Try Again")

def login():
    questions = [
    {
        'type': 'input',
        'name': 'username',
        'message': 'What\'s your username',
    },

    {
        'type': 'password',
        'message': 'Enter your password',
        'name': 'password'
    }
    ]
    answers = prompt(questions, style=custom_style_2)

    print("Logging in ...")
    response = connection_interface.login(answers["username"], answers["password"])

    if response.status_code == 200 and check_timestamp(response.json()["timestamp"]):
        print("Welcome, {}".format(answers["username"]))
        global who 
        who = answers["username"]
    else:
        print(response.json()["message"])
    return response.status_code
    
def options():
    questions = [
    {
        'type': 'list',
        'name': 'option',
        'message': 'What do you want to do',
        'choices' : [
            'View Restaurants',
            'Review Restaurant',
            'View Reviews',
            Separator(),
            'View Vouchers',
            'Transfer Voucher',
            'Use Voucher',
            'Exit'
        ]
    }
    ]
    answers = prompt(questions, style=custom_style_2)

    if answers["option"] == 'View Restaurants':
        global restaurants
        for restaurant in restaurants:
            print(restaurant)
        print()
        return 1
        

    elif answers["option"] == 'View Vouchers':
        vouchers = get_vouchers()

        if not vouchers:
            print()
            print("You don't have any voucher")
            print()
            return 1
        
        print()
        for voucher in vouchers:
            print(voucher[0])
            print(voucher[1])
            print()
        print()
        return 1
    
    elif answers["option"] == 'View Reviews':
        view_reviews()
        return 1
    
    elif answers["option"] == 'Review Restaurant':
        review_restaurant()
        return 1
    
    elif answers["option"] == 'Transfer Voucher':
        transfer_voucher()
        return 1
    
    elif answers["option"] == 'Use Voucher':
        use_voucher()
        return 1
    
    elif answers["option"] == 'Exit':
        return -1

def review_restaurant():
    questions = [
    {
        'type': 'list',
        'name': 'restaurant',
        'message': 'Choose the restaurant you want to review',
        'choices' : restaurants
    }, 
    {
        'type': 'input',
        'name': 'reviewStar',
        'message': 'Insert the review star (From 1 to 5)',
        'validate': ReviewValidator
    },
    {
        'type': 'input',
        'name': 'reviewText',
        'message': 'Insert the review description',
    }
    ]
    answers = prompt(questions, style=custom_style_2)

    rev = {"Star": answers["reviewStar"], "Description" : answers["reviewText"]}
    key = f'keys/users/{who}/private_key.pem'
    signature = generate_signature(json.dumps(rev),key)
    
    response = connection_interface.review(answers["restaurant"], rev ,signature)

    if check_timestamp(response["timestamp"]):
        print(response["message"])
        print()
    else:
        print("Server response failed freshness. Try Again")

def transfer_voucher():
    users = list_users()
    users.remove(who)

    vouchers = get_vouchers()

    choice = []
    restaurant_names = []
    for voucher in vouchers:
        restaurant_names += [voucher[0] ,]
        choice += [''.join(voucher) ,]

    if not choice:
        print()
        print("You don't have any voucher")
        print()
        return
    
    questions = [
    {
        'type': 'list',
        'name': 'User',
        'message': 'Choose the user you want to transfer the Voucher to',
        'choices' : users,
    },
    {
        'type': 'list',
        'name': 'transferredVoucher',
        'message': 'Choose the Voucher you want to transfer',
        'choices' : choice,
    },
    ]
    
    answers = prompt(questions, style=custom_style_2)

    user_ku = connection_interface.requestUserPublicKey(answers["User"])

    if check_timestamp(user_ku["timestamp"]):

        key = f'keys/users/{who}/private_key.pem'

        for voucher in vouchers:
            if voucher[0] in answers["transferredVoucher"]:
                correct_voucher = voucher[1].split(':')
                voucher_obj = {"code": correct_voucher[0], "description": correct_voucher[1]}
                protected_voucher = encrypt_with_public_key(voucher_obj, user_ku["PK"])
                signature = generate_signature(json.dumps(protected_voucher.hex()), key)

                response = connection_interface.transfer_voucher(voucher[0][:-1],protected_voucher.hex(),answers["User"], signature)
                if response["timestamp"]:
                    print(response["message"])
                    print()
                else:
                    print("Server response failed freshness. Try Again")
    else:
        print("Server response failed freshness. Try Again")

def use_voucher():
    vouchers = get_vouchers()
    choice = []
    restaurant_names = []
    for voucher in vouchers:
        restaurant_names += [voucher[0] ,]
        choice += [''.join(voucher) ,]

    if not choice:
        print()
        print("You don't have any voucher")
        print()
        return
    
    questions = [
        {
            'type': 'list',
            'name': 'usedVoucher',
            'message': 'Choose the Voucher you want to redeem',
            'choices' : choice,
        },
        ]
    
    answers = prompt(questions, style=custom_style_2)

    for restaurant in restaurant_names:
        if restaurant in answers["usedVoucher"]:
            restaurant = restaurant[:-1]
            response = connection_interface.use_voucher(restaurant)
            if check_timestamp(response["timestamp"]):
                print(response["message"])
                print()
            else:
                print("Server response failed freshness. Try Again")

def view_reviews():
    questions = [
    {
        'type': 'list',
        'name': 'restaurant',
        'message': 'Choose the restaurant you want to view the review',
        'choices' : restaurants
    }, 
    ]

    answers = prompt(questions, style=custom_style_2)

    response = connection_interface.listReviews(answers["restaurant"])
    if check_timestamp(response["timestamp"]):
        for doc in response["reviews"]:
            rev = json.loads(doc["Review"])
            signature = doc["Signature"]

            if verify_signature(signature, rev, doc["Pu"]):
                print(doc["User"] + " Review: ")
                print("\tStars: " + str(rev["Star"]))
                print("\tDescription: " + rev["Description"])
                print()
            else:
                print(doc["User"] + " Review not authentic!")
    else:
        print("Server response failed freshness. Try Again")


if __name__ == "__main__":
    
    result = login()
    while result == 401:
        result = login()
    if result == 200:
        get_restaurants()
        get_users_keys() #DKD
        answer = options()
        while (answer == 1):
            input("Press Enter to continue")
            answer = options()