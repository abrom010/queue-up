import flask
from flask import jsonify
from flask import request
from flask import flash
import random
import os
import mysql.connector
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import re

# Create Application
application = flask.Flask(__name__)
application.secret_key = 'secret'

# Connect to database
db = mysql.connector.connect(host="35.225.208.225", user="Aaron", passwd="1AsrzsrGJk0l1uEa", db="hackathon")

# Twilio SID Info
account_sid = 'ACf50d76cba4344433156557d73e062105'
auth_token = '5fd058e27df16f50cf47db3f4d4ce732'
client = Client(account_sid, auth_token)

# Route to Homepage at initial Launch
@application.route('/')
def main():
    return flask.render_template('index.html')

# Route to the Map Page
@application.route('/store/')
def store():
    return flask.render_template('storepage.html')

# Generates list of addresses for Google Maps API, happens on the storepage HTML
@application.route('/ids/',methods=['GET'])
def addresses():
    if flask.request.method == 'GET':
        ids = []
        cur = db.cursor()
        # cur.execute("SELECT CONCAT(address, ', ', city, ', ', state, ', ', zip_code) AS FullAddress FROM groceryStores;")
        # for lyst in cur:
        #     addresses.append(lyst[0])
            # print({cur2[i][0]:cur[i][0]})
        cur.execute("SELECT grocery_id FROM groceryStores;")
        for lyst in cur:
            ids.append(lyst[0])
        return jsonify(ids)

# Route to the ticketpage
@application.route('/ticket')
def ticket():
    return flask.render_template('ticketpage.html')

# Get store name, add, csz to populate ticketpage.html
@application.route('/storeData')
def storeData():
    if flask.request.method == 'GET':
        grocID = 3
        result = []
        cur = db.cursor()
        cur.execute('''SELECT store_name, address, city, state, zip_code FROM groceryStores WHERE grocery_id = 3;''', (grocID))
        for i in cur:
            result.append(i)
        return jsonify(result)

# Get queue size to populate ticketpage.html
@application.route('/getSize')
def getSize():
    if flask.request.method == 'GET':
        cur = db.cursor()
        cur.execute('''SELECT MAX(position) FROM queue''')
        result = cur.fetchone()
        return jsonify(result)

# Generates the user to database, when they enter Name and Phone number on ticketpage.
# Then texts them the code and sends them to TicketSuccessPage
@application.route('/storeCust', methods=['POST'])
def storeCust():
    if flask.request.method == 'POST':
        custName = request.form["custName"]
        numb = request.form["numb"]
        numb = formatNumb(numb)
        # return custID, numb
        authToken = random.randint(100000, 999999)
        cur = db.cursor()
        cur.execute('''SELECT MAX(ticket_id), MAX(position) FROM queue''')
        test = cur.fetchone()
        if (test[0]):
            cur.execute('''INSERT INTO queue (ticket_id, cust_name, position, phone_num, authentication) VALUES(%s, %s, %s, %s, %s)''', (test[0] + 1, custName, test[1] + 1, numb, authToken))
        else:
            cur.execute('''INSERT INTO queue (ticket_id, cust_name, position, phone_num, authentication) VALUES(%s, %s, %s, %s, %s)''', (1, custName, 1, numb, authToken))
        db.commit()
        meesage = client.messages.create(
            body = authToken,
            messaging_service_sid = "MGc4338215ff683f8a462df06e206eb8fb",
            to = numb
        )
        flash('Check your phone for your check-in code!')
        # print(numb)
        return flask.render_template('TicketSuccessPage.html')

@application.route('/address', methods=['POST'])
def storeAddress():
    if flask.request.method == 'POST':
        print('post')
        print(request.form)
        for thing in request.form:
            print(thing)
        #groceryID = request.form["groceryID"]
        print(groceryID)
        cur = db.cursor()
        address = cur.execute("SELECT CONCAT(address, ', ', city, ', ', state, ', ', zip_code) AS FullAddress FROM groceryStores WHERE grocery_id = %s;", (groceryID))
        print(address)
        return address

@application.route('/name', methods=['POST'])
def storeName():
    if flask.request.method == 'POST':
        groceryID = request.form["groceryID"]
        cur = db.cursor()
        name = cur.execute("SELECT store_name FROM groceryStores WHERE grocery_id = %s;", (groceryID))
        return name
        
@application.route('/position')
def position():
    return flask.render_template('position.html')

@application.route('/populateTable', methods=['GET'])
def populateTable():
    if flask.request.method == 'GET':
        name = []
        cur = db.cursor()
        cur.execute('''SELECT cust_name FROM queue''')
        for i in cur:
            name.append(i[0])
        return jsonify(name)

# Format the phone number for Twilio
def formatNumb(num):
    print(num)
    num = re.sub("[^0-9]", "", num)
    newNum = "+1" + num
    return newNum

#ONLY RUNS THE FLASK APPLICATION IF THE APP.PY IS BEING USED AS THE DRIVER
if __name__ == '__main__':
    application.run()
