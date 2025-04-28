import argparse
import csv
import json
import requests
import time

def parse_arguments():
    parser = argparse.ArgumentParser(description="PEMFC 센서 데이터를 CSV 파일에서 읽어 POST 전송")
    parser.add_argument('-f', '--file', required=True, help="CSV 파일의 경로 (예: full_csv_data.csv)")
    parser.add_argument('-s', '--start', type=int, required=True, help="CSV 읽기 시작 행(0-based index)")
    parser.add_argument('-e', '--end', type=int, required=True, help="CSV 읽기 끝 행(읽을 마지막 행의 인덱스, end는 포함되지 않음)")
    parser.add_argument('-u', '--url', required=True, help="데이터를 POST할 URL")
    parser.add_argument('-t', '--time', type=float, required=True, help="각 POST 요청 사이의 인터벌(초 단위)")
    return parser.parse_args()

def convert_row_to_json(row):
    """
    CSV의 한 행 데이터를 받아 JSON 스키마에 맞게 변환한다.
    'pw' 필드는 JSON에서 'PW' 키로 대문자 변환한다.
    나머지는 CSV 헤더와 동일한 키명을 사용한다.
    """
    payload = {}
    for key, value in row.items():
        # 값이 숫자형일 경우 숫자 변환을 시도
        try:
            # 소수점이 포함되어 있으면 float, 아니면 int로 변환
            if '.' in value:
                conv_value = float(value)
            else:
                conv_value = int(value)
        except ValueError:
            conv_value = value

        if key == 'pw':
            payload['PW'] = conv_value
        else:
            payload[key] = conv_value

    return payload

def post_data(payload, url):
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        if response.status_code in (200, 201):
            print(f"POST 성공: {payload}")
        else:
            print(f"POST 실패 (상태코드 {response.status_code}): {payload}")
    except Exception as e:
        print(f"POST 요청 중 에러: {e}")

def main():
    args = parse_arguments()

    # CSV 파일 열기 및 읽기
    with open(args.file, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)

        if args.start < 0 or args.end > len(rows):
            print("지정한 범위가 CSV 파일의 행 수를 벗어납니다.")
            return

        # 지정한 범위의 각 행을 순서대로 처리
        for idx in range(args.start, args.end):
            row = rows[idx]
            payload = convert_row_to_json(row)
            print(f"전송할 데이터 (행 {idx}): {payload}")
            post_data(payload, args.url)
            # 지정한 인터벌 만큼 대기
            time.sleep(args.time)

if __name__ == '__main__':
    main()

