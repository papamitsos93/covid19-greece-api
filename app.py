from flask import Flask, jsonify, abort, make_response
from flask_cors import CORS

import json
import copy
import pandas as pd

app = Flask(__name__)
cors = CORS(app)

data_greece_JHCSSE = None
data_greece_isMOOD_regions = None
data_greece_wikipedia = None

def init():
    global data_greece_JHCSSE
    global data_greece_isMOOD_regions
    global data_greece_wikipedia

    with open('data/greece/JohnsHopkinsCSSE/timeseries_greece.json') as f:
        data_greece_JHCSSE = json.load(f)['Greece']
    with open('data/greece/isMOOD/regions.json') as regions_file:
    	data_greece_isMOOD_regions = json.load(regions_file)
    with open('data/greece/wikipedia/cases.csv', encoding = 'utf-8') as cases_file:
    	data_greece_wikipedia = pd.read_csv(cases_file)
    data_greece_wikipedia = data_greece_wikipedia.where(pd.notnull(data_greece_wikipedia), None)

@app.route('/all', methods=['GET'])
def get_all():

    out_json = copy.deepcopy(data_greece_JHCSSE)
    for date in out_json:
        date['active'] = date['confirmed'] - date['deaths'] - date['recovered']

    return jsonify({'cases': out_json})

@app.route('/confirmed', methods=['GET'])
def get_confirmed():

    out_json = copy.deepcopy(data_greece_JHCSSE)
    for date in out_json:
        del date['recovered']
        del date['deaths']

    return jsonify({'cases': out_json})

@app.route('/recovered', methods=['GET'])
def get_recovered():

    out_json = copy.deepcopy(data_greece_JHCSSE)
    for date in out_json:
        del date['confirmed']
        del date['deaths']

    return jsonify({'cases': out_json})

@app.route('/deaths', methods=['GET'])
def get_deaths():

    out_json = copy.deepcopy(data_greece_JHCSSE)
    for date in out_json:
        del date['confirmed']
        del date['recovered']

    return jsonify({'cases': out_json})

@app.route('/regions', methods=['GET'])
def get_regions():

    return jsonify({'regions': data_greece_isMOOD_regions})

@app.route('/active', methods=['GET'])
def get_active():

    out_json = copy.deepcopy(data_greece_JHCSSE)
    for date in out_json:
        date['active'] = date['confirmed'] - date['deaths'] - date['recovered']
        del date['confirmed']
        del date['recovered']
        del date['deaths']


    return jsonify({'cases': out_json})


@app.route('/total', methods=['GET'])
def get_total():
    out_json = copy.deepcopy(data_greece_JHCSSE[-1])
    out_json['active'] = out_json['confirmed'] - out_json['deaths'] - out_json['recovered']

    return jsonify({'cases': out_json})


@app.route('/total-tests', methods=['GET'])
def get_total_tests():

    date = list(data_greece_wikipedia['Date'])[:-1]
    total_tests = list(data_greece_wikipedia['Cumulative tests performed'])[:-1]
    total_tests = [int(i) if i!=None else None for i in total_tests]
    out_json = [{'date': date, 'tests':tests} for date, tests in zip(date, total_tests)]

    return jsonify({'total-tests': out_json})

@app.route('/intensive-care', methods=['GET'])
def get_intensive_care():

    date = list(data_greece_wikipedia['Date'])[:-1]
    intensive_care = list(data_greece_wikipedia['In intensive care (total)'])[:-1]
    intensive_care = [int(i) if i!=None else None for i in intensive_care]
    out_json = [{'date': date, 'intensive-care':num_patients} for date, num_patients in zip(date, intensive_care)]

    return jsonify({'intensive-care': out_json})

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    init()
    app.run(debug=True)
