import json
import time
import requests
from dataclasses import dataclass
from pathlib import Path

class QuotaExceeded(Exception):
    pass

@dataclass
class EmergencyInfoApiConfig:
    api_relative_url: str
    output_dir: Path
    year_month_key: str

class EmergencyInfoApiClient:
    BASE_URL = "http://apis.data.go.kr/1661000/EmergencyInformationService/"

    MAX_RPS = 10
    ROWS = 4000
    REQUEST_TIMEOUT = 120.0

    ATTEMPTS = 3
    REATTEMPT_BASE_DELAY = 2.0

    SKIPPED = -1

    def __init__(self, config: EmergencyInfoApiConfig):
        self.config = config

        self.url = self.BASE_URL + self.config.api_relative_url

        self.session = requests.Session()

        self._next_call_time = 0.0

        self.config.output_dir.mkdir(parents=True, exist_ok=True)

    def close(self):
        if self.session is not None:
            self.session.close()
            self.session = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def _wait_until_request_allowed(self):
        now = time.monotonic()

        if now < self._next_call_time:
            time.sleep(self._next_call_time - now)

        now = time.monotonic()

        self._next_call_time = (
            max(now, self._next_call_time) + 1.0 / self.MAX_RPS
        )

    def _request_page(self, api_key: str,
                      station: str, year_month: str, page_no: int) -> object:
        self._wait_until_request_allowed()

        params = {
            "serviceKey": api_key,
            "numOfRows": self.ROWS,
            "pageNo": page_no,
            "resultType": "json",
            "rsacGutFsttOgidNm": station,
            self.config.year_month_key: year_month,
        }

        response = self.session.get(self.url,
                                    params=params,
                                    timeout=self.REQUEST_TIMEOUT)

        response.raise_for_status()

        response_text = response.text.lstrip()

        if response_text.startswith("<"):
            if "LIMITED_NUMBER_OF_SERVICE_REQUESTS" in response_text:
                raise QuotaExceeded(
                    f"Quota exceeded: {station} {year_month}"
                )

            raise RuntimeError(
                f"{station} {year_month} - Unexpected XML response: {response_text[:500]}"
            )

        try:
            return response.json()
        except ValueError as error:
            raise RuntimeError(
                f"{station} {year_month} - Invalid JSON response.") from error

    def fetch_month(self, api_key: str, station: str, year_month: str)\
        -> tuple[str, str, int]:
        station_dir = self.config.output_dir / station
        station_dir.mkdir(parents=True, exist_ok=True)

        save_path = station_dir / f"{station}_{year_month}.json"

        if save_path.exists():
            return (station, year_month, self.SKIPPED)

        collected = []
        page_no = 1

        while True:
            payload = self._request_page(api_key, station, year_month, page_no)

            try:
                body = payload["body"]
                items = body.get("items") or []
                total_count = int(payload.get("totalCount", 0))
            except (KeyError, TypeError, ValueError) as error:
                raise RuntimeError(
                    f"{station} {year_month} - Unexpected API response."
                    ) from error

            if not items:
                if page_no == 1:
                    print(f"{station} {year_month} - No items found.")
                break

            collected.extend(items)

            print(
                f"{station} {year_month} - page={page_no}; "
                f"collected={len(collected)}/{total_count}"
            )

            if len(collected) >= total_count:
                break

            page_no += 1

        self._save_json(save_path, collected)

        return (station, year_month, len(collected))

    def _save_json(self, save_path: Path, data: list[object]) -> None:
        temp_path = save_path.with_suffix(".json.tmp")

        with temp_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

        temp_path.replace(save_path)

    def fetch_month_with_retry(self, api_key: str, station: str, year_month: str)\
        -> tuple[str, str, object]:
        for attempt in range(1, self.ATTEMPTS + 1):
            try:
                return self.fetch_month(api_key, station, year_month)

            except QuotaExceeded:
                raise

            except Exception as error:
                if attempt == self.ATTEMPTS:
                    return (station, year_month, f"All attempts failed: {error}")

                delay = self.REATTEMPT_BASE_DELAY ** (attempt - 1)

                print(
                    f"Retrying {station} {year_month} ({attempt}/{self.ATTEMPTS}) "
                    f"in {delay:.1f}s: {error}"
                )

                time.sleep(delay)

        raise RuntimeError("Invalid input for attempts.")

    def fetch_all(self, api_key: str, stations: list[str], months: list[str]):
        tasks = [(station, month) for station in stations for month in months]
        failures = []

        started_at = time.time()

        for current, (station, month) in enumerate(tasks, start=1):
            try:
                _, _, result = self.fetch_month_with_retry(api_key, station, month)

            except QuotaExceeded as error:
                print(f"Stopped: {error}")
                break

            if isinstance(result, str):
                failures.append((station, month, result)
                )

            if current % 50 == 0:
                elapsed = time.time() - started_at

                print(
                    f"Progress: [{current}/{len(tasks)}]; "
                    f"Elapsed: {elapsed:.0f}s; "
                    f"Failures: {len(failures)}"
                )

        self._print_result(failures)
        return failures

    def _print_result(self, failures):
        if not failures:
            print("Ended with no failures.")
            return

        print(f"Ended with {len(failures)} failures:")

        for failure in failures:
            print(failure)
