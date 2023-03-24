import requests
import csv
import json
import dateutil.parser
from dateutil.tz import UTC
import time


anchorage_tz = dateutil.tz.gettz("America/Anchorage")


def parse_api(f):
    data = []
    delimiter = f[0][4]
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
                    time_with_zone = time_wo_zone.replace(tzinfo=anchorage_tz)
                    data_entry[header.lower()] = time_with_zone.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
                case _:
                    data_entry[header.lower()] = line[headers.index(header)]
        data.append(data_entry)
    return data


def main():
    areas = ["Eagle River", "Kincaid Park", "Far North Bicentennial Park", "Bear Valley", "Fire Island"]
    for line in areas:
        url = f"https://incommodities.io/a?area={line}"

        payload = {}
        headers = {
            "Authorization": "Bearer dd47a765605d473fa89c1510c767697d"
        }

        response = requests.post(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Bad request return value: {response}")
        data = parse_api(response.text.split('\n'))
        print(data)
        if len(data) < 3:
            raise Exception(f"Bad data {data}")
        data.reverse()
        jsonob = {
            "area": f"{line}",
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


if __name__ == '__main__':
    while True:
        try:
            main()
            time.sleep(60)
        except Exception as e:
            print(e)
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
