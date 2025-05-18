import argparse
import csv
import json
import requests
import time

def parse_arguments():
    parser = argparse.ArgumentParser(description="PEMFC 센서 데이터를 CSV 파일에서 읽어 POST 전송")
    parser.add_argument('-f', '--file', required=True, help="CSV 파일의 경로 (예: full_csv_data.csv)")
    parser.add_argument('-p1', '--pemfc1', type=int, required=True, help="pemfc1의 id")
    parser.add_argument('-p2', '--pemfc2', type=int, required=True, help="pemfc2의 id")
    parser.add_argument('-p3', '--pemfc3', type=int, required=True, help="pemfc3의 id")
    parser.add_argument('-s1', '--start1', type=int, required=True, help="pemfc1의 CSV 읽기 시작 행(0-based index)")
    parser.add_argument('-s2', '--start2', type=int, required=True, help="pemfc2의 CSV 읽기 시작 행(0-based index)")
    parser.add_argument('-s3', '--start3', type=int, required=True, help="pemfc3의 CSV 읽기 시작 행(0-based index)")
    parser.add_argument('-o', '--offset', type=int, required=True, help="CSV에서 읽어올 행 수")
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

        total_rows = len(rows)

        # 각 PEMFC별 URL 구성
        url1 = args.url.replace("{pemfc_id}", str(args.pemfc1))
        url2 = args.url.replace("{pemfc_id}", str(args.pemfc2))
        url3 = args.url.replace("{pemfc_id}", str(args.pemfc3))

        # 모든 시작 인덱스 + offset이 범위 내에 있는지 확인
        for start in [args.start1, args.start2, args.start3]:
            if start < 0 or (start + args.offset) > total_rows:
                print(f"지정한 시작 인덱스 {start} 또는 범위가 CSV 데이터 수({total_rows}행)를 벗어납니다.")
                return

        for i in range(args.offset):
            idx1 = args.start1 + i
            idx2 = args.start2 + i
            idx3 = args.start3 + i

            row1 = rows[idx1]
            row2 = rows[idx2]
            row3 = rows[idx3]

            payload1 = convert_row_to_json(row1)
            payload2 = convert_row_to_json(row2)
            payload3 = convert_row_to_json(row3)

            print(f"[{i}] PEMFC1 행 {idx1}: {payload1}")
            post_data(payload1, url1)

            print(f"[{i}] PEMFC2 행 {idx2}: {payload2}")
            post_data(payload2, url2)

            print(f"[{i}] PEMFC3 행 {idx3}: {payload3}")
            post_data(payload3, url3)

            time.sleep(args.time)

if __name__ == '__main__':
    main()

