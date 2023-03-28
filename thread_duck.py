"""This module solves InCommodities case."""

import csv
import datetime
import time
import threading
import requests
from dateutil.parser import isoparse
from dateutil.tz import UTC
from dateutil.tz import gettz
import json
import queue

successQ = queue.Queue()
errorQ = queue.Queue()
class Logger:
    """"Write logs to a given file"""

    def __init__(self, filename: str):
        """Constructor for Logger:
            Expects a filename (string)."""
        self.filename = filename

    def log(self, message: str):
        """Write message to text file"""
        with open(self.filename, "a", encoding="utf-8") as file:
            file.write(datetime.datetime.now().strftime(
                "%Y %m %d - %H:%M:%S \n"))
            file.write(message)
            file.write("\n\n")


def process_area(area, data=None):
    """Process an entire area. Tries again if it errors.
        Handles exceptions itself"""
    print(f"processing: {area}")
    # if data is already given then the make_request has been made
    if data is None:
        code = -1
        while code == -1:
            try:
                (data, code, _) = make_request(area)
            except requests.exceptions.ReadTimeout as err:
                print(str(err))
            except Exception as error:
                (error_message, response_text) = error.args
                print(f"Exception: {error_message}")
                errorQ.put(f"The error message is {str(error_message)} with data:\n{response_text}")
            if code == -1:
                # request is already known. Wait 5 seconds and try again.
                print("Waiting 0.1 seconds before trying again :)")
                time.sleep(0.1)
    send_to_api(data, area)


def main():
    """Main immediately checks if new data exist.
        If it does, then all is pulled, parsed
        and sent to the other api. If not then it
        waits 5 seconds and tries again."""

    areas = ["Eagle River", "Kincaid Park",
             "Far North Bicentennial Park", "Bear Valley", "Fire Island"]

    # check if there is new data.
    print("Starting duck :)")
    forecast_time: datetime = datetime.datetime.now().astimezone(UTC) - datetime.timedelta(seconds=100)
    p_diff = 0
    while True:
        difference = (datetime.datetime.now().astimezone(UTC) - forecast_time).total_seconds()
        if p_diff != int(difference):
            print(int(difference))
            p_diff = int(difference)
        if difference > 59.5:
            code = -1
            data = []
            while code == -1:
                try:
                    (data, code, forecast_time) = make_request(areas[0])
                except requests.exceptions.ReadTimeout as err:
                    print(str(err))
                except Exception as error:
                    (error_message, response_text) = error.args
                    print(f"Exception: {error_message}")
                    errorQ.put(f"The error message is {str(error_message)} with data:\n{response_text}")
                if code == -1:
                    print("Waiting 0.1 seconds before trying again :)")
                    time.sleep(0.1)
            print("Got new data. Trying to fetch all the others.")
            print(datetime.datetime.now().astimezone(UTC))
            print(forecast_time)
            startThreads(data)
            print(f"Latency was {(datetime.datetime.now().astimezone(UTC) - forecast_time).total_seconds()} seconds")
        time.sleep(0.05)


def make_request(area: str):
    """Makes a request to the url and returns
        the parsed form as JSON.
        Returns -1 if the data is not valid.
        :raises Exception for bad response"""

    get_url = "https://incommodities.io/a"
    headers_get = {
        "Authorization": "Bearer dd47a765605d473fa89c1510c767697d"
    }
    response = requests.post(f"{get_url}?area={area}", headers=headers_get, timeout=0.5)
    if response.status_code != 200:
        raise Exception(
            f"Bad response code for response: {str(response)}", response.text)
    if does_exist(response.text):
        return [], -1, 0
    (data_json, forecast_time) = parse_csv_to_json(response.text.split("\n"))
    successQ.put(f"The current area is {area}:\n{response.text}")
    return data_json, 0, forecast_time


def send_to_api(data, area):
    """Sends the given data to the API correctly formatted"""

    send_url = "https://incommodities.io/b"
    headers_send = {
        "Authorization": "Bearer dd47a765605d473fa89c1510c767697d",
        "Content-Type": "application/json"
    }
    requests.post(send_url, headers=headers_send, data=json.dumps({
        "area": area,
        "forecast": data
    }))
    print(f"successfully sent {area}")


def parse_csv_to_json(csv_file):
    """Checks if the file given is valid and
        parses to JSON. It also returns the forecast time.
        :raises Exception
            - for bad delimiter"""

    anchorage_tz = gettz("America/Anchorage")

    delimiter = csv_file[0][4]
    if delimiter not in ["|", ",", ";", "🐻", "_"]:
        response = "\n".join(csv_file)
        raise Exception(f"Bad delimiter: '{delimiter}", response)

    csv_reader = csv.reader(csv_file, delimiter=delimiter)
    headers = next(csv_reader)
    parsed = []
    forecast_time = None
    for line in csv_reader:
        entry = {}
        for header in headers:
            match header:
                case "Forecast time":
                    if forecast_time is None:
                        time_wo_zone = None
                        try:
                            time_wo_zone = isoparse(
                                line[headers.index(header)])
                        except Exception as error:
                            raise Exception(
                                f"Not valid time format: {str(error)}", "\n".join(csv_file))
                        time_with_zone = time_wo_zone.replace(tzinfo=anchorage_tz)
                        forecast_time = time_with_zone.astimezone(UTC)
                case "Time":
                    time_wo_zone = None
                    try:
                        time_wo_zone = isoparse(
                            line[headers.index(header)])
                    except Exception as error:
                        raise Exception(
                            f"Not valid time format: {str(error)}", "\n".join(csv_file))
                    time_with_zone = time_wo_zone.replace(tzinfo=anchorage_tz)
                    new_time = time_with_zone.astimezone(
                        UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
                    entry[header.lower()] = new_time
                case _:
                    entry[header.lower()] = line[headers.index(header)]
        parsed.append(entry)
    return parsed, forecast_time


def does_exist(response: str):
    """Check if the given response already has
        been parsed.
        :raises Exception when handling file."""

    responses = ""
    with open("success.log", "r", encoding="utf-8") as file:
        responses = file.read()
    responses = responses.split("\n\n")
    responses = ["\n".join(x.split("\n")[2:]) for x in responses]
    return response in responses


def startThreads(data):
    i = 0
    threads = [threading.Thread(target=process_area, args=("Kincaid Park", None)),
               threading.Thread(target=process_area, args=("Far North Bicentennial Park", None)),
               threading.Thread(target=process_area, args=("Bear Valley", None)),
               threading.Thread(target=process_area, args=("Fire Island", None))]

    for thread in threads:
        print(f"starting thread {str(i)}")
        i = i + 1
        thread.start()
    process_area("Eagle River", data)
    for thread in threads:
        thread.join()
    print("joining threads")
    emptyQ()

def emptyQ():
    while not errorQ.empty():
        errorLog = Logger("error.log")
        errorLog.log(errorQ.get())
        print("emptying failq")
    while not successQ.empty():
        successLog = Logger("success.log")
        successLog.log(successQ.get())
        print("emptying sucessQ")

if __name__ == "__main__":
    main()
