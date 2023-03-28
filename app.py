from flask import Flask, request
from flask_cors import CORS
from duck import parse_csv_to_json
import json

app = Flask(__name__)
CORS(app)

# fetch(url=127.0.0.1:8001/{area})
data = {}


@app.get("/<area>")
def return_data(area):
    return data[area]


with open("save.log", "r") as file:
    areas = ["Eagle_River", "Bear_Valley", "Fire_Island", "Far_north_Bicentennial_Park", "Kincaid_Park"]
    areas_csv = file.read().split("\n\n")[-6:-1] # få fem sidste
    for area in areas_csv:
        index = areas_csv.index(area)
        area = area.split("\n")[2:]
        (data_json, forecast_time) = parse_csv_to_json(area)
        data[areas[index]] = json.dumps(data_json)
print(data)

