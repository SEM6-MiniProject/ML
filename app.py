import pickle
from flask import Flask, request, jsonify
from helper import file_processing

app = Flask(__name__)
with open("./model/anemia.pkl", "rb") as f:
    lod_pickle = pickle.load(f)


@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route("/predict")
def predict():
    json = request.get_json()
    gender = json["Gender"]
    hemoglobin = json["Hemoglobin"]
    mch = json["MCH"]
    mchc = json["MCHC"]
    mcv = json["MCV"]
    to_predict = [gender, hemoglobin, mch, mchc, mcv]
    to_predict = [to_predict]
    prediction = lod_pickle.predict(to_predict)

    return jsonify(prediction=prediction.tolist()[0])


@app.route("/predict_file", methods=["POST"])
def predict_file():
    file = request.files["file"]
    file_extension = file.filename.split(".")[-1]
    file_name = file.filename.split(".")[0]
    file.save(f"{file_name}.{file_extension}")
    prediction = file_processing(f"{file_name}.{file_extension}")
    if isinstance(prediction, str):
        return jsonify(prediction=prediction)
    req_data = {
        "gender": 1,
        "Hemoglobin": prediction["Hemoglobin"],
        "MCH": prediction["MCH"],
        "MCHC": prediction["MCHC"],
        "MCV": prediction["MCV"],
    }
    to_predict = list(req_data.values())
    to_predict = [float(i) for i in to_predict]
    to_predict = [to_predict]
    prediction = lod_pickle.predict(to_predict)
    return jsonify(prediction=prediction.tolist()[0])


if __name__ == "__main__":
    app.run(debug=True)
