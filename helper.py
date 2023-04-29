import sqlite3
from PIL import Image
import pytesseract
import configuration

# pylint: disable=too-many-boolean-expressions
# pylint: disable=no-else-return


def ocr_processing(filename):

    text = pytesseract.image_to_string(
        Image.open(filename), config="--psm 12 --oem 3"
    )  # We'll use Pillow's Image class to open the image and pytesseract to detect the string in the image

    return text


def insert_into_db(patient_data_dict):

    con = sqlite3.connect("./Lab_Reports.db", timeout=10)
    if con:
        print("OK")
    else:
        print("NOT OK")

    cur = con.cursor()
    h = patient_data_dict["Hemoglobin"]
    pcv = patient_data_dict["PCV"]
    rbc = patient_data_dict["RBC"]
    mcv = patient_data_dict["MCV"]
    mch = patient_data_dict["MCH"]
    mchc = patient_data_dict["MCHC"]
    rdw = patient_data_dict["RDW"]
    tlc = patient_data_dict["TLC"]
    pc = patient_data_dict["Platelet_Count"],
    gender = patient_data_dict["Gender"]
    # check if table exists or not
    cur.execute(
        "SELECT count(name) FROM sqlite_master WHERE type='table' AND name='CITY_PATHOLOGY_LAB_FEVER_PANEL'"
    )
    if cur.fetchone()[0] == 1:
        print("Table exists.")
    else:
        print("Table does not exist.")
        sql_query = "CREATE TABLE CITY_PATHOLOGY_LAB_FEVER_PANEL (Patient_Name varchar(100) NOT NULL,Hemoglobin varchar(100) NOT NULL,PCV varchar(100) NOT NULL,RBC varchar(100) NOT NULL,MCV varchar(100) NOT NULL,MCH varchar(100) NOT NULL,MCHC varchar(100) NOT NULL,RDW varchar(100) NOT NULL,TLC varchar(100) NOT NULL,Platelet_Count varchar(100) NOT NULL,status,username varchar(100) NOT NULL,dates varchar(100) NOT NULL,gender varchar(100) NOT NULL)"
        cur.execute(sql_query)

    # try:
    #     sql_query = "CREATE TABLE CITY_PATHOLOGY_LAB_FEVER_PANEL (Patient_Name varchar(100) NOT NULL,Hemoglobin varchar(100) NOT NULL,PCV varchar(100) NOT NULL,RBC varchar(100) NOT NULL,MCV varchar(100) NOT NULL,MCH varchar(100) NOT NULL,MCHC varchar(100) NOT NULL,RDW varchar(100) NOT NULL,TLC varchar(100) NOT NULL,Platelet_Count varchar(100) NOT NULL,status,username varchar(100) NOT NULL,dates varchar(100) NOT NULL)"
    #     cur.execute(sql_query)
    # except Exception as e:
    #     print(e)
    print("Table created successfully")
    if (
        (float(h) >= 14 and float(h) <= 18)
        and (float(pcv) >= 35 and float(pcv) <= 90)
        and (float(rbc) >= 4.5 and float(rbc) <= 6)
        and (float(mcv) >= 82 and float(mcv) <= 98)
        and (float(mch) >= 27 and float(mch) < 31)
        and (float(mchc) >= 32 and float(mchc) <= 36)
        and (float(rdw) >= 11 and float(rdw) <= 16)
        and (float(tlc) >= 4.5 and float(tlc) <= 11)
        and (float(pc) >= 150 and float(pc) <= 450)
    ):
        sql_query = "INSERT INTO CITY_PATHOLOGY_LAB_FEVER_PANEL (Patient_Name,Hemoglobin,PCV,RBC,MCV,MCH,MCHC,RDW,TLC,Platelet_Count,status,username,dates,gender) VALUES (?,?,?,?,?,?,?,?,?,?,'rejected',?,DateTime('now'),?)"
        cur.execute(
            sql_query,
            (
                patient_data_dict["Patient_Name"],
                patient_data_dict["Hemoglobin"],
                patient_data_dict["PCV"],
                patient_data_dict["RBC"],
                patient_data_dict["MCV"],
                patient_data_dict["MCH"],
                patient_data_dict["MCHC"],
                patient_data_dict["RDW"],
                patient_data_dict["TLC"],
                patient_data_dict["Platelet_Count"],
                patient_data_dict["username"],
                patient_data_dict["gender"]
            ),
        )

    elif (
        (float(h) < 14 or float(h) > 18)
        or (float(pcv) < 35 or float(pcv) > 90)
        or (float(rbc) < 4.5 or float(rbc) > 6)
        or (float(mcv) < 82 or float(mcv) > 98)
        or (float(mch) < 27 or float(mch) > 31)
        or (float(mchc) < 32 or float(mchc) > 36)
        or (float(rdw) < 11 or float(rdw) > 16)
        or (float(tlc) < 4.5 or float(tlc) > 11)
        or (float(pc) < 150 or float(pc) > 450)
    ):
        sql_query = "INSERT INTO CITY_PATHOLOGY_LAB_FEVER_PANEL (Patient_Name,Hemoglobin,PCV,RBC,MCV,MCH,MCHC,RDW,TLC,Platelet_Count,status,username,dates,gender) VALUES (?,?,?,?,?,?,?,?,?,?,'accepted',?,DateTime('now'),?)"
        cur.execute(
            sql_query,
            (
                patient_data_dict["Patient_Name"],
                patient_data_dict["Hemoglobin"],
                patient_data_dict["PCV"],
                patient_data_dict["RBC"],
                patient_data_dict["MCV"],
                patient_data_dict["MCH"],
                patient_data_dict["MCHC"],
                patient_data_dict["RDW"],
                patient_data_dict["TLC"],
                patient_data_dict["Platelet_Count"],
                patient_data_dict["username"],
                patient_data_dict["Gender"]
            ),
        )

    con.commit()
    con.close()


def file_processing(filename):

    try:

        # Python-tesseract is a wrapper for Google’s Tesseract-OCR Engine. Here we connect with tesseract, which installed on system

        # pytesseract.pytesseract.tesseract_cmd = (
        #     r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        # )
        # For docker image
        pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
        # Passing image to ocr_processing function

        data = ocr_processing(filename)

        # Converting string to list by using split function, where \n is used as split parameter

        data_extracted_from_image = data.split("\n")

        # Creating new list list_without_null_values, where all null values are removed

        list_without_null_values = [i for i in data_extracted_from_image if i]

        # Data in list along with index

        # for index, value in enumerate(list_without_null_values):
        #    print(index, value)

        # Check if the repory belongs to approved lab and test

        if (list_without_null_values[0] in configuration.approved_labs) and (
            list_without_null_values[21].replace("Test Name : ", "")
            in configuration.approved_tests
        ):

            # Creating dict with report details

            default_dict = {
                "Lab_Name": list_without_null_values[0],
                "Patient_Name": list_without_null_values[4],
                "Gender": list_without_null_values[13],
                "Test_Name": list_without_null_values[21],
                "Hemoglobin": list_without_null_values[28],
                "PCV": list_without_null_values[32],
                "RBC": list_without_null_values[36],
                "MCV": list_without_null_values[40],
                "MCH": list_without_null_values[44],
                "MCHC": list_without_null_values[48],
                "RDW": list_without_null_values[52],
                "TLC": list_without_null_values[56],
                "Platelet_Count": list_without_null_values[102],
                "username": list_without_null_values[108],
            }

            insert_into_db(default_dict)
            # print(default_dict)

            text = (
                "Submitted Reports of Patient Name :- " + default_dict["Patient_Name"]
            )

            return default_dict

        else:

            text = "Invalid File Report"

            return text

    except Exception as e:
        print("-->> ", e)
        print(e)
        text = "Error occurred during file processing!!"

        return text
