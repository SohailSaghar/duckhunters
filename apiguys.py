import requests
import csv
import json
import dateutil.parser
from dateutil.tz import UTC
import datetime
import time
import threading
import schedule
import queue

"""                                                                                                                                                                                                   ,--,                                                                    
DDDDDDDDDDDDD                                              kkkkkkkk                HHHHHHHHH     HHHHHHHHH                                           tttt                                                                   
D::::::::::::DDD                                           k::::::k                H:::::::H     H:::::::H                                        ttt:::t                                                                   
D:::::::::::::::DD                                         k::::::k                H:::::::H     H:::::::H                                        t:::::t                                                                   
DDD:::::DDDDD:::::D                                        k::::::k                HH::::::H     H::::::HH                                        t:::::t                                                                   
  D:::::D    D:::::D uuuuuu    uuuuuu      cccccccccccccccc k:::::k    kkkkkkk       H:::::H     H:::::H  uuuuuu    uuuuuunnnn  nnnnnnnn    ttttttt:::::ttttttt        eeeeeeeeeeee    rrrrr   rrrrrrrrr       ssssssssss   
  D:::::D     D:::::Du::::u    u::::u    cc:::::::::::::::c k:::::k   k:::::k        H:::::H     H:::::H  u::::u    u::::un:::nn::::::::nn  t:::::::::::::::::t      ee::::::::::::ee  r::::rrr:::::::::r    ss::::::::::s  
  D:::::D     D:::::Du::::u    u::::u   c:::::::::::::::::c k:::::k  k:::::k         H::::::HHHHH::::::H  u::::u    u::::un::::::::::::::nn t:::::::::::::::::t     e::::::eeeee:::::eer:::::::::::::::::r ss:::::::::::::s 
  D:::::D     D:::::Du::::u    u::::u  c:::::::cccccc:::::c k:::::k k:::::k          H:::::::::::::::::H  u::::u    u::::unn:::::::::::::::ntttttt:::::::tttttt    e::::::e     e:::::err::::::rrrrr::::::rs::::::ssss:::::s
  D:::::D     D:::::Du::::u    u::::u  c::::::c     ccccccc k::::::k:::::k           H:::::::::::::::::H  u::::u    u::::u  n:::::nnnn:::::n      t:::::t          e:::::::eeeee::::::e r:::::r     r:::::r s:::::s  ssssss 
  D:::::D     D:::::Du::::u    u::::u  c:::::c              k:::::::::::k            H::::::HHHHH::::::H  u::::u    u::::u  n::::n    n::::n      t:::::t          e:::::::::::::::::e  r:::::r     rrrrrrr   s::::::s      
  D:::::D     D:::::Du::::u    u::::u  c:::::c              k:::::::::::k            H:::::H     H:::::H  u::::u    u::::u  n::::n    n::::n      t:::::t          e::::::eeeeeeeeeee   r:::::r                  s::::::s   
  D:::::D    D:::::D u:::::uuuu:::::u  c::::::c     ccccccc k::::::k:::::k           H:::::H     H:::::H  u:::::uuuu:::::u  n::::n    n::::n      t:::::t    tttttte:::::::e            r:::::r            ssssss   s:::::s 
DDD:::::DDDDD:::::D  u:::::::::::::::uuc:::::::cccccc:::::ck::::::k k:::::k        HH::::::H     H::::::HHu:::::::::::::::uun::::n    n::::n      t::::::tttt:::::te::::::::e           r:::::r            s:::::ssss::::::s
D:::::::::::::::DD    u:::::::::::::::u c:::::::::::::::::ck::::::k  k:::::k       H:::::::H     H:::::::H u:::::::::::::::un::::n    n::::n      tt::::::::::::::t e::::::::eeeeeeee   r:::::r            s::::::::::::::s 
D::::::::::::DDD       uu::::::::uu:::u  cc:::::::::::::::ck::::::k   k:::::k      H:::::::H     H:::::::H  uu::::::::uu:::un::::n    n::::n        tt:::::::::::tt  ee:::::::::::::e   r:::::r             s:::::::::::ss  
DDDDDDDDDDDDD            uuuuuuuu  uuuu    cccccccccccccccckkkkkkkk    kkkkkkk     HHHHHHHHH     HHHHHHHHH    uuuuuuuu  uuuunnnnnn    nnnnnn          ttttttttttt      eeeeeeeeeeeeee   rrrrrrr              sssssssssss    


"""


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
    if delimiter not in ["|", ",", ";", "🐻", "_"]:
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
                    new_time = time_with_zone.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
                    data_entry[header.lower()] = new_time
                case _:
                    data_entry[header.lower()] = line[headers.index(header)]
        data.append(data_entry)
    return data


# Error and success handling
errorsLog = Logger("errors.log")
successLog = Logger("success.log")

failQ = queue.Queue()
succQ = queue.Queue()


def request(timezone, area):
    successful = False
    # Standard post request
    url = f"https://incommodities.io/a?area={area}"
    headers = {
        "Authorization": "Bearer dd47a765605d473fa89c1510c767697d"
    }
    while not successful:
        print("requesting from server " + area)
        response = requests.post(url, headers=headers, timeout=2)
        # Checking for bad response status code. If anything than 200 (OK status code) raise an exception.
        if response.status_code != 200:
            failQ.put(f"This response is from {area}. Bad request return value: {response.text}")
            time.sleep(1)
            continue
        # from csv to json format
        try:
            data = parse_api(response.text.split('\n'), timezone)
        except Exception as e:
            continue
        # successful = True
        if len(data) < 3:
            failQ.put(f"This data is from {area}. Bad data {data}: \n{response.text}")
            continue
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
        # requests.request("POST", sendurl, headers=headers, data=payload)

        # Only log a new request if it is different from the last one
        old_data = False
        with open("success.log", "r") as f:
            responses = f.read().split("\n\n")
            responses = ["\n".join(x.split("\n")[2:]) for x in responses]
            if response.text in responses:
                old_data = True
        if old_data:
            print("Old data received. Not logging again.")
            time.sleep(1)
            continue
        else:
            succQ.put(f"This data is from {area}:\n{response.text}")
            print(f"Success! {area} data sent to server\n")
            requests.request("POST", sendurl, headers=headers, data=payload)
            successful = True



# Starting threads for each area
def startThreads(threads):
    i = 0
    start = time.time()
    for thread in threads:
        print(f"starting thread {str(i)}")
        thread.start()
    request(anchorage_tz, "Fire Island")
    emptyQ()
    for thread in threads:
        thread.join()
    print(f"\ntime taken with threads: {time.time() - start}")


def emptyQ():
    while not failQ.empty():
        errorsLog.log(failQ.get())
    while not succQ.empty():
        successLog.log(succQ.get())


if __name__ == '__main__':
    anchorage_tz = dateutil.tz.gettz("America/Anchorage")
    errorLog = Logger("errors.log")
    areas = ["Eagle River", "Kincaid Park", "Far North Bicentennial Park", "Bear Valley", "Fire Island"]

    threads = [threading.Thread(target=request, args=(anchorage_tz, areas[0])),
               threading.Thread(target=request, args=(anchorage_tz, areas[1])),
               threading.Thread(target=request, args=(anchorage_tz, areas[2])),
               threading.Thread(target=request, args=(anchorage_tz, areas[3]))]
    # for loop to make an array of times to start threads
    startTimers = []
    for i in range(0, 24):
        if i < 10:
            startTimers.append(f"0{i}:00")
            startTimers.append(f"0{i}:30")
        else:
            startTimers.append(f"{i}:00")
            startTimers.append(f"{i}:30")
    for thirty_min in startTimers:
        schedule.every().day.at(thirty_min).do(startThreads, threads)

    while True:
        try:
            schedule.run_pending()
        except Exception as e:
            print(str(e).split("\n")[0])
            errorLog.log(str(e))
            print("I will try again later :)")
            time.sleep(2)
        time.sleep(0.1)