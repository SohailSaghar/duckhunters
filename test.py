sample = """Time,Forecast time,Temperature,Humidity,Wind,Pressure
2023-03-26T01:00:00,2023-03-25T00:31:23,21.3,41.51,5.2,49.972
2023-03-26T00:00:00,2023-03-25T00:31:23,59.6,42.78,8.6,41.951
2023-03-25T23:00:00,2023-03-25T00:31:23,-1,37.23,3.6,34.578
2023-03-25T22:00:00,2023-03-25T00:31:23,-55.7,49.54,7.5,48.286
2023-03-25T21:00:00,2023-03-25T00:31:23,26.7,34.82,4.6,44.842
2023-03-25T20:00:00,2023-03-25T00:31:23,16.8,45.53,3,44.327
2023-03-25T19:00:00,2023-03-25T00:31:23,67.5,38.37,5,30.153
2023-03-25T18:00:00,2023-03-25T00:31:23,59.2,65.1,5.5,37.132
2023-03-25T17:00:00,2023-03-25T00:31:23,-27,30.57,6.2,34.442
2023-03-25T16:00:00,2023-03-25T00:31:23,-11.5,36.5,1.5,35.466
2023-03-25T15:00:00,2023-03-25T00:31:23,-24.2,42.5,5.1,43.084
2023-03-25T14:00:00,2023-03-25T00:31:23,-17.2,64.78,3.5,46.734
2023-03-25T13:00:00,2023-03-25T00:31:23,42.1,63.7,6.9,31.097
2023-03-25T12:00:00,2023-03-25T00:31:23,-11.3,50.95,7.8,34.177
2023-03-25T11:00:00,2023-03-25T00:31:23,-38.3,62.74,3.1,41.581
2023-03-25T10:00:00,2023-03-25T00:31:23,85,60.89,6.7,40.739
2023-03-25T09:00:00,2023-03-25T00:31:23,49.7,48.08,4.6,35.777
2023-03-25T08:00:00,2023-03-25T00:31:23,58.7,36.33,7,30.939
2023-03-25T07:00:00,2023-03-25T00:31:23,71.9,37.41,7.2,47.643
2023-03-25T06:00:00,2023-03-25T00:31:23,34.4,68.22,1.3,30.232
2023-03-25T05:00:00,2023-03-25T00:31:23,-19,38.8,6.6,49.346
2023-03-25T04:00:00,2023-03-25T00:31:23,-7.5,36.77,2.9,32.377
2023-03-25T03:00:00,2023-03-25T00:31:23,75,33.16,8.2,42.907
2023-03-25T02:00:00,2023-03-25T00:31:23,68.2,56.96,1.1,29.458"""

old_data = False
with open("success.log", "r") as f:
    responses = f.read().split("\n\n")
    responses = ["\n".join(x.split("\n")[2:]) for x in responses]
    # print("\n".join(responses[4].split("\n")[1:]))
    print(responses[4] == sample)
    print(responses[4])
    print("CHANGE")
    print(sample)
    print(sample in responses)
    if sample in responses:
        old_data = True
if old_data:
    print("Old data received. Not logging again.")
else:
    print("New data :)")
    # with open("success.log" , "a" ) as f:
    #     f.write (response.text + "\n\n")