import pickle
from flask import Flask, request, jsonify

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


if __name__ == "__main__":
    app.run(debug=True)
