from flask import Flask, request, render_template, redirect, url_for, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import pymongo

app = Flask(__name__)

# Connect to the MongoDB database
client = pymongo.MongoClient(
                      os.environ.get('client'), 
                      # username= os.environ.get('username'), 
                      # password=os.environ.get('password'),
)
db = client['tracking_database']
packages_collection = db['packages']
locations_collection = db['locations']
drivers_collection = db['drivers']


@app.route('/')
def home():
  return render_template('index.html')

@app.route('/get_drivers', methods=['GET'])
def get_drivers():
  # Query the drivers collection
  drivers = list(drivers_collection.find())

  # Return the list of drivers as a JSON response
  return jsonify({'status': 'success', 'drivers': drivers}) 

@app.route('/add_driver')
def add_driver_form():
  return render_template('driver.html')

@app.route('/add_driver', methods=['POST'])
def add_driver():
  # Get the driver's information from the form
  name = request.form['name']
  email = request.form['email']
  phone = request.form['phone']

  # Create a new document in the drivers collection
  driver = {
    'name': name,
    'email': email,
    'phone': phone
  }

  # Save the driver to the database
  drivers_collection.insert_one(driver)

  return redirect(url_for('driver_added'))

@app.route('/driver_added')
def driver_added():
  return render_template('driver.html')

@app.route('/add_package')
def add_package_form():
  return render_template('form.html')

@app.route('/add_package', methods=['POST'])
def add_package():
  # Get the package information from the form
  package_id = request.form['package_id']
  location = request.form['location']
  # Add any other relevant details here

  # Save the package information in the database
  package = {
    'package_id': package_id,
    'location': location,
    # Add any other relevant details here
  }
  packages_collection.insert_one(package)

  return redirect(url_for('track_package', package_id=package_id))

@app.route('/assign_package', methods=['POST'])
def assign_package():
  # Get the package ID from the request body
  data = request.get_json()
  package_id = data['package_id']

  # Assign the package to the driver here (e.g. update the database)

  return jsonify({'status': 'success'})


@app.route('/track_package/<package_id>')
def track_package(package_id):
  # Get the package information from the database
  package = packages_collection.find_one({'package_id': package_id})

  # Get the current location of the package
  location = locations_collection.find_one({'package_id': package_id})['location']

  return render_template('index.html', package=package, location=location)

@app.route('/update_location', methods=['POST'])
def update_location():
  # Get the package ID and location from the request body
  data = request.get_json()
  package_id = data['package_id']
  location = data['location']

  # Save the location in the database
  locations_collection.update_one({'package_id': package_id}, {'$set': {'location': location}}, upsert=True)

  return jsonify({'status': 'success'})

@app.route('/get_location', methods=['POST'])
def get_location():
  # Get the package ID of the package whose location is being requested
  data = request.get_json()
  package_id = data['package_id']

  # Get the location from the database
  location = locations_collection.find_one({'package_id': package_id})

  if location:
    return jsonify({'status': 'success', 'location': location['location']})
  else:
    return jsonify({'status': 'error', 'message': 'Location not found'})

if __name__ == '__main__':
  app.run(debug=True)
