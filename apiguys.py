import requests
import csv
import json
import dateutil.parser
from dateutil.tz import UTC
import datetime
import time


class Logger:
    def __init__(self, filename):
        self.filename = filename

    def log(self, message):
        with open(self.filename, "a") as f:
            f.write(datetime.datetime.now().strftime("%Y %m %d - %H:%M:%S \n"))
            f.write(message)
            f.write("\n\n")


def parse_api(f, timezone):
    data = []
    delimiter = f[0][4]
    if delimiter not in ["|", ",", ";"]:
        response = "\n".join(f)
        raise Exception(f"Bad delimiter: '{delimiter}'\n{response}")
    csv_reader = csv.reader(f, delimiter=delimiter)
    headers = csv_reader.__next__()
    for line in csv_reader:
        data_entry = {}
        for header in headers:
            match header:
                case "Forecast time":
                    pass
                case "Time":
                    time_wo_zone = dateutil.parser.isoparse(line[headers.index(header)])
                    time_with_zone = time_wo_zone.replace(tzinfo=timezone)
                    data_entry[header.lower()] = time_with_zone.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
                case _:
                    data_entry[header.lower()] = line[headers.index(header)]
        data.append(data_entry)
    return data


def main(timezone):
    # Areas
    areas = ["Eagle River", "Kincaid Park", "Far North Bicentennial Park", "Bear Valley", "Fire Island"]
    # Error and success handling
    errorsLog = Logger("errors.log")
    successLog = Logger("success.log")

    for area in areas:
        # Standard post request
        url = f"https://incommodities.io/a?area={area}"
        headers = {
            "Authorization": "Bearer dd47a765605d473fa89c1510c767697d"
        }
        response = requests.post(url, headers=headers)
        # Checking for bad response status code. If anything than 200 (OK status code) raise an exception.
        if response.status_code != 200:
            raise Exception(f"This response is from {area} \nBad request return value: {response.text}")
        # from csv to json format
        data = parse_api(response.text.split('\n'), timezone)
        if len(data) < 3:
            raise Exception(f"This data is from {area}.\nBad data {data}: \n{response.text}")
        data.reverse()
        print(data)
        jsonob = {
            "area": f"{area}",
            "forecast": data
        }
        datafile = json.dumps(jsonob, indent=2)
        sendurl = "https://incommodities.io/b"

        payload = datafile
        headers = {
            'Authorization': 'Bearer dd47a765605d473fa89c1510c767697d',
            'Content-Type': 'application/json'
        }
        requests.request("POST", sendurl, headers=headers, data=payload)
        # Only log a new request
        successLog.log(f"This data is from {area}:\n{response.text}")


if __name__ == '__main__':
    anchorage_tz = dateutil.tz.gettz("America/Anchorage")
    errorLog = Logger("errors.log")
    while True:
        try:
            main(anchorage_tz)
            time.sleep(60)
        except Exception as e:
            print(str(e).split("\n")[0])
            print("I will try again later :)")
            time.sleep(2)


# now = dateutil.parser.parse("2013/11-07")
# print(now)
#
# url = "https://incommodities.io/a/"
# token = dd47a765605d473fa89c1510c767697d
# header = {"Authorization": f"Bearer {token}"}
# while 3 < 2:
#     if(datetime.datetime.now().minute == 30):
#         startReq()
#
# def startReq():
#     request = requests.post(URL, headers=header)
