from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Category, CategoryItem, engine
from functools import wraps

from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from flask import make_response
import httplib2
import json
import string
import random
import requests


app = Flask(__name__)

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = 'Fullstack nano item'

APP_SECRET_KEY = 'bEbhsr5dkUeSVyto3jWl'


# Decorator function for authentication verification
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in login_session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('show_login'))
    return decorated_function


# Create anti-forgery state token
@app.route('/login')
def show_login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state, CLIENT_ID=CLIENT_ID)


# Google auth endpoint (connect)
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Getting an access token
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # check whether token's client ID match app's or not
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')

    # if user already connected
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps("This user is already connected."),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    # Save user data in login_session
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width:100px; height:100px; border-radius:150px;">'
    return output


# Google auth endpoint (disconnect)
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')

    # check current access token
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
          % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    # if user logged and want to disconnect, remove his login_session data
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps(
            'Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('catalog'))
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'

    return redirect(url_for('catalog'))


# Get one catalog item in JSON format
@app.route('/catalog_items/<int:item_id>/JSON')
def catalog_item_json(item_id):
    item = session.query(CategoryItem).filter_by(id=item_id).one()
    return jsonify(item.serialize)


# Get all catalog items in JSON format
@app.route('/catalog_items/JSON')
def catalog_items_json():
    items = session.query(CategoryItem).all()
    return jsonify(catalog_items=[r.serialize for r in items])


# Get one catalog category in JSON format
@app.route('/catalog_categories/<int:category_id>/JSON')
def catalog_category_json(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    return jsonify(category.serialize)


# Get all catalog categories in JSON format
@app.route('/catalog_categories/JSON')
def catalog_categories_json():
    categories = session.query(Category).all()
    return jsonify(catalog_categories=[r.serialize for r in categories])


# Get whole catalog data in JSON format
@app.route('/catalog/JSON')
def catalog_json():
    items = session.query(CategoryItem).all()
    categories = session.query(Category).all()
    return jsonify(catalog_categories=[r.serialize for r in items],
                   catalog_items=[r.serialize for r in categories])


# Get whole catalog
@app.route('/')
@app.route('/catalog/', methods=['GET'])
def catalog():
    categories = session.query(Category).all()
    latest_catalog_items = session.query(CategoryItem)\
        .order_by(CategoryItem.created_date.desc())\
        .limit(4).all()

    return render_template('index.html',
                           categories=categories,
                           items=latest_catalog_items)


# Get all items of category
@app.route('/catalog/<int:category_id>/items/', methods=['GET'])
def category_items(category_id):
    categories = session.query(Category).all()
    items = session.query(CategoryItem)\
        .filter_by(category_id=category_id).all()
    return render_template('index.html',
                           categories=categories,
                           items=items,
                           selected_category=category_id)


# Preview an item description
@app.route('/catalog/<int:category_id>/<int:item_id>/',
           methods=['GET'])
def preview_category_item(category_id, item_id):
    current_item = session.query(CategoryItem).filter_by(
        id=item_id,
        category_id=category_id).one()
    return render_template('item-preview.html',
                           item=current_item)


# Create a new catalog item
@app.route('/catalog/new-menu-item/', methods=['GET', 'POST'])
@login_required
def create_category_item():
    if request.method == 'POST':
        newItem = CategoryItem(name=request.form['name'],
                               description=request.form['description'],
                               category_id=request.form['category'])
        session.add(newItem)
        session.commit()

        return redirect(url_for('catalog'))
    else:
        categories = session.query(Category).all()
        return render_template('item-create.html',
                               categories=categories)


# Edit an item if logged in
@app.route('/catalog/<int:category_id>/<int:item_id>/edit',
           methods=['GET', 'POST'])
@login_required
def edit_category_item(category_id, item_id):
    edited_item = session.query(CategoryItem).filter_by(
        id=item_id,
        category_id=category_id).one()
    categories = session.query(Category).all()

    if request.method == 'POST':
        if request.form['name']:
            edited_item.name = request.form['name']
        if request.form['description']:
            edited_item.description = request.form['description']
        if request.form['category']:
            edited_item.category_id = request.form['category']

        session.add(edited_item)
        session.commit()

        return redirect(url_for('catalog'))
    else:
        return render_template('item-edit.html',
                               item=edited_item,
                               categories=categories)


# Delete an item if logged in
@app.route('/catalog/<int:category_id>/<int:item_id>/delete',
           methods=['GET', 'POST'])
@login_required
def delete_category_item(category_id, item_id):
    deleted_item = session.query(CategoryItem).filter_by(
        id=item_id,
        category_id=category_id).one()

    if request.method == 'POST':
        session.delete(deleted_item)
        session.commit()

        return redirect(url_for('catalog'))
    else:
        return render_template('item-delete.html',
                               item=deleted_item,
                               category_id=category_id)


if __name__ == '__main__':
    app.secret_key = APP_SECRET_KEY
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
