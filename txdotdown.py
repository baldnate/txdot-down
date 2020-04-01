import json
import requests
import base64
import re
import time

# human website:
# http://its.txdot.gov/ITS_WEB/FrontEnd/default.html?r=AUS&p=Austin&t=cctv

# from https://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename
def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    value = re.sub('[-\s]+', '-', value)
    # ...
    return value

def decode_chunk(chunk):
  if "Offline" in chunk[-1]:
    return False
  return chunk[-2]

def chunk_GetCctvDataOfArea(lst):
  yield_val = list()
  for i in lst.split(","):
    yield_val.append(i)
    if "Device " in i:
      chonk = decode_chunk(yield_val)
      if chonk:
        yield chonk
      yield_val = list()

def download_cam(cctv_id, filename=False):
  if filename is False:
    filename = slugify(cctv_id) + ".jpg"

  r = requests.post(
    'http://its.txdot.gov/ITS_WEB/FrontEnd/svc/DataRequestWebService.svc/GetCctvContent', 
    json = { "arguments": cctv_id + ",1" }
  )

  response = r.text.split(",")

  if len(response) > 2 and response[2] == "Device Online":
    try:
      image = bytearray(base64.b64decode(response[4][0:-1]))
    except:
      print(response)
      return
    open(filename, "wb").write(image)
    time.sleep(10)
  else:
    print(r.text)

r = requests.post(
  'http://its.txdot.gov/ITS_WEB/FrontEnd/svc/DataRequestWebService.svc/GetCctvDataOfArea', 
  json = {"arguments":"AUS,30.859,-98.011265,29.80436,-97.314"}
)

while True:
  for cctv_id in chunk_GetCctvDataOfArea(r.text):
    print("fetching " + cctv_id)
    download_cam(cctv_id, "cctv.jpg")
