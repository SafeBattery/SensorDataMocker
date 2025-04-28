from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/sensor', methods=['POST'])
def echo_sensor_data():
    # POST 요청의 JSON 데이터를 가져옴
    data = request.get_json()
    if data is None:
        return jsonify({"error": "JSON 데이터가 필요합니다."}), 400

    # 받은 데이터를 로그 출력
    app.logger.info("Received data: %s", data)
    
    # 에코 응답: 받은 데이터를 다시 전송
    return jsonify({"status": "success", "data": data}), 200

if __name__ == "__main__":
    # 기본적으로 로컬 5000번 포트에서 실행
    app.run(host='0.0.0.0', port=5000, debug=True)

