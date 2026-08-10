import requests
import json
import time
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

URL = "http://apis.data.go.kr/1661000/EmergencyInformationService/" \
    "getEmgPatientTransferInfo"
KEY = os.getenv("DATA_API_KEY")

STATIONS = ['강남소방서', '강동소방서', '노원소방서',
            '수성소방서', '해운대소방서', '원주소방서']

MONTHS = [f"{year}{month:02d}"
          for year in range(2017, 2026)
          for month in range(1, 13)]

MAX_RPS = 10 # less than 30 tps
WORKERS = 4
ROWS = 4000
OUT = './data/raw/구급환자이송정보';

os.makedirs(OUT, exist_ok=True)

SKIPPED = -1 # already present

class QuotaExceeded(Exception):
    pass

_next_callable_time = 0.0

def wait_until_call_allowed():
    global _next_callable_time
    now = time.monotonic()
    if now < _next_callable_time:
        time.sleep(_next_callable_time - now)
    _next_callable_time = max(now, _next_callable_time) + 1.0 / MAX_RPS

def request_page(station, year_month, page_no):
    wait_until_call_allowed()

    request_params = {
        'serviceKey': KEY,
        'numOfRows': ROWS,
        'pageNo': page_no,
        'resultType': 'json',
        'rsacGutFsttOgidNm': station,
        'stmtYm': year_month
        }

    response = requests.get(URL, timeout=120.0, params=request_params)

    response_text = response.text.lstrip()

    if response_text.startswith('<'):
        if 'LIMITED_NUMBER_OF_SERVICE_REQUESTS' in response_text:
            raise QuotaExceeded(f"Quota exceeded: {station} {year_month}.")
        raise RuntimeError(f"{station} {year_month} - {response_text}")

    return response.json()

def fetch_month(station, year_month):
    save_path = f"{OUT}/{station}/{station}_{year_month}.json"
    if os.path.exists(save_path):
        return station, year_month, SKIPPED

    collected = []
    page_no = 1

    while True:
        payload = request_page(station, year_month, page_no)
        page_items = payload['body']['items'] or None

        if not page_items:
            print(f"{station} {year_month} - No page items found.")
            break

        collected.extend(page_items)

        if len(collected) >= payload['totalCount']:
            break

        page_no += 1

    with open(save_path, 'w', encoding='utf-8') as file:
        json.dump(collected, file, ensure_ascii=False)

    return station, year_month, len(collected)

def fetch_month_with_attempts(station, year_month, attempts=3):
    for attempt in range(attempts):
        try:
            return fetch_month(station, year_month)
        except QuotaExceeded:
            raise
        except Exception as error:
            if attempt + 1 == attempts:
                return station, year_month, f"All attempts failed: {error}"
            time.sleep(2.0 ** attempt)

    raise ValueError("attempts need to be greater than 1.")

tasks = [(station, year_month) for station in STATIONS for year_month in MONTHS]

failures = []
started_at = time.time()

for completed, (station, year_month) in enumerate(tasks, 1):
    try:
        os.makedirs(f"{OUT}/{station}", exist_ok=True)
        station, year_month, result = fetch_month_with_attempts(station, year_month)
    except QuotaExceeded as error:
        print(f"Stopped: {error}")
        break

    if isinstance(result, str):
        failures.append((station, year_month, result))

    if completed % 50 == 0:
        elapsed = time.time() - started_at
        print(f"Progress: [{completed}/{len(tasks)}]\tElasped Time: {elapsed:.0f} s\tFailures: {len(failures)}")

if not failures:
    print("Ended with no failures.")
else:
    print(f"Ended with {len(failures)} failures:")
    print(failures)
