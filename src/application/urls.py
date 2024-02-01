from flask import Blueprint
from .controllers import (
    keys_controller,
    login_controller,
    documents_controller,
    review_controller,
    reviews_controller,
    users_controller,
    voucher_controller,
    transfer_voucher_controller,
    user_controller, 
    restaurant_controller
)
from ..app import app

# Define URL routes
@app.route('/login', methods=['POST'])
def login():
    return login_controller()

@app.route('/documents', methods=['GET'])
def documents():
    return documents_controller()

@app.route('/review', methods=['POST'])
def review():
    return review_controller()

@app.route('/reviews', methods=['GET'])
def reviews():
    return reviews_controller()

@app.route('/users', methods=['GET'])
def users():
    return users_controller()

@app.route('/user', methods=['GET'])
def user():
    return user_controller()

@app.route('/voucher', methods=['DELETE'])
def voucher():
    return voucher_controller()

@app.route('/transfer_voucher', methods=['PUT'])
def transfer_voucher():
    return transfer_voucher_controller()

@app.route('/restaurant', methods=['GET'])
def restaurant():
    return restaurant_controller()

@app.route('/keys', methods=['GET'])
def keys():
    return keys_controller()