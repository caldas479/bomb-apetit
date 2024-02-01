import copy
import json
from flask import jsonify, request, session

from src.security_library.algos import read_key, verify_signature, generate_signature, check_timestamp, create_timestamp
from ..bd_session import Document, User, Session

#Base = declarative_base()

db_session = Session()

def login_controller():
    timestamp = create_timestamp()
    data = request.get_json()
    if not data or 'usr' not in data or 'pswd' not in data or 'timestamp' not in data:
        return jsonify({'message': 'Invalid request. Provide usr: username and pswd: password in JSON.', 'timestamp' : timestamp}), 400
    
    if not check_timestamp(data.get('timestamp')):
        return jsonify({'message': 'Invalid request. Request is not fresh, either you are doing a Reply Attack or there\'s a bad connection.', 'timestamp' : timestamp}), 418

    usr = data.get('usr')
    pswd = data.get('pswd')

    user = db_session.query(User).filter_by(username=usr, password=pswd).first()
    timestamp = create_timestamp()
    if user:
        session['logged_in_user'] = user.id
        return jsonify({'message': 'Login successful!', 'timestamp' : timestamp}), 200
    else:
        return jsonify({'message': 'Login failed! Invalid credentials.', 'timestamp' : timestamp}), 401
    
def keys_controller():
    timestamp = create_timestamp()
    data = request.get_json()
    if not data or 'timestamp' not in data:
        return jsonify({'message': 'Invalid request. Provide timestamp in JSON.', 'timestamp' : timestamp}), 400
    
    if not check_timestamp(data.get('timestamp')):
        return jsonify({'message': 'Invalid request. Request is not fresh, either you are doing a Reply Attack or there\'s a bad connection.', 'timestamp' : timestamp}), 418

    logged_in_user = session.get('logged_in_user')
    if logged_in_user:
        keys_path = db_session.query(User.public_key).all()
        keys = []
        for path in keys_path:    
            keys += [{'val': read_key(path[0]), 'path': path[0]}]

        timestamp = create_timestamp()
        return jsonify({"keys": keys, "timestamp" : timestamp}) ,200
    
    return jsonify({"message": "User not logged.", "timestamp" : timestamp}), 404

def documents_controller():
    timestamp = create_timestamp()
    data = request.get_json()
    if not data or 'timestamp' not in data:
        return jsonify({'message': 'Invalid request. Provide timestamp in JSON.', 'timestamp' : timestamp}), 400
    
    if not check_timestamp(data.get('timestamp')):
        return jsonify({'message': 'Invalid request. Request is not fresh, either you are doing a Reply Attack or there\'s a bad connection.', 'timestamp' : timestamp}), 418

    logged_in_user = session.get('logged_in_user')
    timestamp = create_timestamp()
    if logged_in_user:
        documents = db_session.query(Document).filter_by(user_id=logged_in_user).all()
        document_list = []
        for doc in documents:
            document_info = {
                "Restaurant Name": doc.restaurant_name,
                "Text": doc.protected_document
            }
            document_list.append(document_info)

        return jsonify({"documents" : document_list, "timestamp" : timestamp}), 200
    else:
        return jsonify({"message": "User not logged.", "timestamp" : timestamp}), 404

def review_controller():
    data = request.get_json()
    timestamp = create_timestamp()
    if not data or 'restaurant' not in data or 'review' not in data or 'signature' not in data or 'timestamp' not in data:
        return jsonify({'message': 'Invalid request. Provide restaurant: name and review:JSON and signature.', 'timestamp' : timestamp}), 400
    
    if not check_timestamp(data.get('timestamp')):
        return jsonify({'message': 'Invalid request. Request is not fresh, either you are doing a Reply Attack or there\'s a bad connection.', 'timestamp' : timestamp}), 418

    logged_in_user = session.get('logged_in_user')

    if logged_in_user:
        rev = data.get("review")
        signature = data.get("signature")
        user_public_key = db_session.query(User).filter_by(id=logged_in_user).first().public_key
       
        if not verify_signature(signature, rev, user_public_key):
          return jsonify({'message': 'Review is not authentic.', 'timestamp' : timestamp}), 401

        doc = db_session.query(Document).filter_by(user_id=logged_in_user, restaurant_name=data.get('restaurant')).first()
        if doc:
            doc.review = json.dumps(rev)
            doc.review_signature = signature
            db_session.commit()
            return jsonify({'message': 'Review added successfully.', 'timestamp' : timestamp}), 200

        return jsonify({'message': 'Restaurant not found.', 'timestamp' : timestamp}), 404 

    return jsonify({'message': 'User not logged in.', 'timestamp' : timestamp}), 404

def reviews_controller():
    timestamp = create_timestamp()
    data = request.get_json()
    if not data or 'restaurant' not in data or 'timestamp' not in data:
        return jsonify({'message': 'Invalid request. Provide restaurant: name in JSON.', 'timestamp' : timestamp}), 400
    
    if not check_timestamp(data.get('timestamp')):
        return jsonify({'message': 'Invalid request. Request is not fresh, either you are doing a Reply Attack or there\'s a bad connection.', 'timestamp' : timestamp}), 418

    logged_in_user = session.get('logged_in_user')
    if not logged_in_user:
        return jsonify({"message": "User not logged.", 'timestamp' : timestamp}), 404
    
    docs = db_session.query(Document).filter_by(restaurant_name=data.get('restaurant')).all()
    reviews = [{'Review':doc.review, 'Signature': doc.review_signature, 'User': db_session.query(User).filter_by(id=doc.user_id).first().username, 'Pu':db_session.query(User).filter_by(id=doc.user_id).first().public_key} for doc in docs if doc.review and doc.review_signature]
    timestamp = create_timestamp()
    return jsonify({"reviews" : reviews, "timestamp" : timestamp}) , 200

def users_controller():
    timestamp = create_timestamp()
    data = request.get_json()
    if not data or 'timestamp' not in data:
        return jsonify({'message': 'Invalid request. Provide timestamp in JSON.', 'timestamp' : timestamp}), 400
    
    if not check_timestamp(data.get('timestamp')):
        return jsonify({'message': 'Invalid request. Request is not fresh, either you are doing a Reply Attack or there\'s a bad connection.', 'timestamp' : timestamp}), 418
    
    logged_in_user = session.get('logged_in_user')

    if logged_in_user:
        users = db_session.query(User).all()
        users_list = [{'User Name': user.username} for user in users]
        return jsonify({"Users" : users_list, "timestamp" : timestamp}), 200
    else:
        return jsonify({"message": "User not logged.", "timestamp" : timestamp}), 404
    
def voucher_controller():
    timestamp = create_timestamp()
    data = request.get_json()
    if not data or 'restaurant' not in data or 'timestamp' not in data:
        return jsonify({'message': 'Invalid request. Provide voucher value in JSON.', 'timestamp' : timestamp}), 400
    
    if not check_timestamp(data.get('timestamp')):
        return jsonify({'message': 'Invalid request. Request is not fresh, either you are doing a Reply Attack or there\'s a bad connection.', 'timestamp' : timestamp}), 418

    logged_in_user = session.get('logged_in_user')

    if logged_in_user:
        document_to_update = db_session.query(Document).filter_by(user_id=logged_in_user, restaurant_name=data.get('restaurant')).first()

        if document_to_update:
            document_to_update.protected_document = None
            db_session.commit()
            return jsonify({'message': 'Voucher redeemed successfully.', 'timestamp' : timestamp}), 200
        else:
            return jsonify({'message': 'Voucher not found.', 'timestamp' : timestamp}), 404
    else:
        return jsonify({"message": "User not logged in.", 'timestamp' : timestamp}), 404
    
def transfer_voucher_controller():
    timestamp = create_timestamp()
    data = request.get_json()
    if not data or 'restaurant' not in data or 'voucher' not in data or 'user' not in data or 'signature' not in data or 'timestamp' not in data:
        return jsonify({'message': 'Invalid request. Provide restaurant name, voucher document and username in JSON.', 'timestamp' : timestamp}), 400
    
    if not check_timestamp(data.get('timestamp')):
        return jsonify({'message': 'Invalid request. Request is not fresh, either you are doing a Reply Attack or there\'s a bad connection.', 'timestamp' : timestamp}), 418

    logged_in_user = session.get('logged_in_user')
    if not logged_in_user:
        return jsonify({"message": "User not logged in.", 'timestamp' : timestamp}), 404

    dest_user = db_session.query(User).filter_by(username=data.get('user')).first()
    if not dest_user:
        return jsonify({"message": "User not found.", 'timestamp' : timestamp}), 404

    doc_dest = db_session.query(Document).filter_by(user_id=dest_user.id, restaurant_name=data.get('restaurant')).first()
    if doc_dest.protected_document:
        return jsonify({"message": "User already has a voucher.", 'timestamp' : timestamp}), 404

    doc_source = db_session.query(Document).filter_by(user_id=logged_in_user, restaurant_name=data.get('restaurant')).first()
    if not doc_source.protected_document:
        return jsonify({"message": "You don't have that Voucher.", 'timestamp' : timestamp}), 404
    
    user = db_session.query(User).filter_by(id=logged_in_user).first()

    signature = data.get('signature')
    voucher = data.get('voucher')

    timestamp = create_timestamp()

    if not verify_signature(signature, voucher, user.public_key):
        return jsonify({'message': 'Voucher is not authentic.', 'timestamp' : timestamp}), 401

    restaurant = data.get('restaurant')
    restaurant_key = f'keys/restaurants/{restaurant}/private_key.pem'

    protected_document_src = json.loads(doc_source.protected_document)

    protected_document_dest = copy.deepcopy(protected_document_src)
    protected_document_dest.pop("signature")
    protected_document_dest["restaurantInfo"]["mealVoucher"] = voucher

    restaurant_signature = generate_signature(json.dumps(protected_document_dest), restaurant_key)
    protected_document_dest["signature"] = restaurant_signature
    
    doc_dest.protected_document = json.dumps(protected_document_dest)
    doc_source.protected_document = None    

    db_session.commit()

    return jsonify({'message': f'Voucher transferred successfully to {dest_user.username}.', 'timestamp' : timestamp}), 200

def user_controller():
    timestamp = create_timestamp()
    data = request.get_json()
    if not data or 'user' not in data or 'timestamp' not in data:
        return jsonify({'message': 'Invalid request. Provide user name in JSON.', 'timestamp' : timestamp}), 400
    
    if not check_timestamp(data.get('timestamp')):
        return jsonify({'message': 'Invalid request. Request is not fresh, either you are doing a Reply Attack or there\'s a bad connection.', 'timestamp' : timestamp}), 418

    logged_in_user = session.get('logged_in_user')
    if not logged_in_user:
        return jsonify({"message": "User not logged in.", 'timestamp' : timestamp}), 404
    
    dest_user = db_session.query(User).filter_by(username=data.get('user')).first()
    if not dest_user:
        return jsonify({"message": "User not found.", 'timestamp' : timestamp}), 404
    
    return jsonify({"PK" : dest_user.public_key, 'timestamp' : timestamp})

def restaurant_controller():
    timestamp = create_timestamp()
    data = request.get_json()
    if not data or 'restaurant' not in data:
        return jsonify({'message': 'Invalid request. Provide restaurant name in JSON.', 'timestamp' : timestamp}), 400
    
    if not check_timestamp(data.get('timestamp')):
        return jsonify({'message': 'Invalid request. Request is not fresh, either you are doing a Reply Attack or there\'s a bad connection.', 'timestamp' : timestamp}), 418

    logged_in_user = session.get('logged_in_user')
    if not logged_in_user:
        return jsonify({"message": "User not logged in.", 'timestamp' : timestamp}), 404
    
    rest = db_session.query(Document).filter_by(restaurant_name=data.get('restaurant')).first()
    if not rest:
        return jsonify({"message": "Restaurant not found.", 'timestamp' : timestamp}), 404
    
    return jsonify({"RPK" : rest.restaurant_public_key, 'timestamp' : timestamp})