import json
import os
import time

#import bs4
import requests
from flask import Flask, request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sqlalchemy import func, and_, or_, not_

from db import Course
from db import db

options = Options()
options.headless = True
options.add_argument("--window-size=1920,1080")

app = Flask(__name__)
db_filename = "funclass.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

# initialize app
db.init_app(app)
with app.app_context():
    db.create_all()


# generalized response formats
def success_response(data, code=200):
    return json.dumps({"success": True, "data": data}), code


def failure_response(message, code=404):
    return json.dumps({"success": False, "error": message}), code


@app.route("/api/courses/<course_subj>/<course_code>/")
def get_course(course_subj, course_code):
    course = Course.query.filter_by(subj=course_subj, code=course_code).first()
    if course is None:
        return failure_response('Course not found')
    return success_response(course.serialize())


# Not for the faint of heart: updates all classes, rewrites entire database, requires about three hours.
@app.route("/api/internal/update/", methods=["POST"])
def update_web_data():
    body = json.loads(request.data)
    proceed = body.get('CONFIRM', False)
    if not proceed:
        return failure_response("Confirmation required.")
    semester = 'FA21'
    # pull data from online
    departments = requests.get("https://classes.cornell.edu/api/2.0/config/subjects.json", params={"roster": semester})
    json_depts = departments.json()
    for dept in json_depts['data']['subjects']:
        class_subj = dept['value']
        dept_class = requests.get("https://classes.cornell.edu/api/2.0/search/classes.json",
                                  params={"roster": semester, "subject": class_subj})
        json_classes = dept_class.json()
        if json_classes['status'] == "error":
            return failure_response("Subject not found")
        
        for each_class in json_classes['data']['classes']:
            class_code = int(each_class['catalogNbr'])
            class_name = each_class['titleLong']
            class_desc = each_class['description']
            if class_desc is None:
                class_desc = ''
            class_credits = each_class['enrollGroups']
            if class_credits is not None:
                class_credits = class_credits[0]
                if class_credits is not None:
                    class_credits = class_credits['unitsMinimum']
            if class_credits is None:
                class_credits = 0
            class_credits = int(class_credits)
            
            timeload = 0.5
            errorload = True
            while errorload and timeload <= 3:
                driver = webdriver.Chrome(options=options, executable_path="./chromedriver_90")
                driver.get("https://www.cureviews.org/course/" + class_subj + "/" + str(class_code))
                time.sleep(timeload)
                CURs = driver.find_elements_by_class_name('gauge-text-top')
                
                class_CURover = -1
                class_CURdiff = -1
                class_CURwork = -1
                
                if len(CURs) == 3:
                    class_CURover = CURs[0].text
                    class_CURdiff = CURs[1].text
                    class_CURwork = CURs[2].text
                    errorload = False
                else:
                    CRED = '\033[91m'
                    CEND = '\033[0m'
                    print(CRED + "Error, did not load! Retrying!" + CEND)
                    timeload += 3
                driver.quit()
            
            if class_CURover == '-':
                class_CURover = -1
            if class_CURdiff == '-':
                class_CURdiff = -1
            if class_CURwork == '-':
                class_CURwork = -1
            
            class_CURover = float(class_CURover)
            class_CURdiff = float(class_CURdiff)
            class_CURwork = float(class_CURwork)
            new_course = Course(subject=class_subj, code=class_code, name=class_name, description=class_desc,
                                credits=class_credits, overall=class_CURover, difficulty=class_CURdiff,
                                workload=class_CURwork)
            # print(new_course.serialize())
            # print((class_CURover, class_CURdiff, class_CURwork))
            db.session.add(new_course)
        db.session.commit()
    
    return success_response(None)


@app.route("/api/internal/update/<course_subj>/<course_code>/")
def update_single_class(course_subj, course_code):
    semester = 'FA21'
    # pull data from online
    dept_class = requests.get("https://classes.cornell.edu/api/2.0/search/classes.json",
                              params={"roster": semester, "subject": course_subj})
    
    json_classes = dept_class.json()
    if json_classes['status'] == "error":
        return failure_response("Subject not found")
    
    for each_class in json_classes['data']['classes']:
        class_code = each_class['catalogNbr']
        if class_code != str(course_code):
            continue
        
        desired_course = Course.query.filter_by(subj=course_subj, code=course_code).first()
        if desired_course is None:
            return failure_response('Course not found')
        
        class_code = int(class_code)
        class_name = each_class['titleLong']
        class_desc = each_class['description']
        if class_desc is None:
            class_desc = ''
        class_credits = each_class['enrollGroups']
        if class_credits is not None:
            class_credits = class_credits[0]
            if class_credits is not None:
                class_credits = class_credits['unitsMinimum']
        if class_credits is None:
            class_credits = 0
        class_credits = int(class_credits)
        
        timeload = 0.5
        errorload = True
        while errorload and timeload <= 4:
            driver = webdriver.Chrome(options=options, executable_path="./chromedriver_90")
            driver.implicitly_wait(2)
            driver.get("https://www.cureviews.org/results/keyword/" + course_subj)
            driver.get("https://www.cureviews.org/course/" + course_subj + "/" + str(class_code))
            time.sleep(timeload)
            #innerHTML = driver.execute_script("return document.body.innerHTML")
            #time.sleep(timeload)
            #root = bs4.BeautifulSoup(innerHTML, "lxml")  # parse HTML using beautifulsoup
            #viewcount = root.find_all("span", attrs={'class': 'gauge-text-top'})
            CURs = driver.find_elements_by_class_name('gauge-text-top')
            #print(driver.execute_script("return document.body.innerHTML;"))
            
            class_CURover = -1
            class_CURdiff = -1
            class_CURwork = -1
            
            if len(CURs) == 3:
                class_CURover = CURs[0].text
                class_CURdiff = CURs[1].text
                class_CURwork = CURs[2].text
                errorload = False
            else:
                CRED = '\033[91m'
                CEND = '\033[0m'
                print(CRED + "Error, did not load! Retrying!" + CEND)
                timeload += 3
            driver.quit()
        
        if class_CURover == '-':
            class_CURover = -1
        if class_CURdiff == '-':
            class_CURdiff = -1
        if class_CURwork == '-':
            class_CURwork = -1
        
        class_CURover = float(class_CURover)
        class_CURdiff = float(class_CURdiff)
        class_CURwork = float(class_CURwork)

        desired_course.subj = course_subj
        desired_course.code = class_code
        desired_course.desc = class_desc
        desired_course.credits = class_credits
        desired_course.CURover = class_CURover
        desired_course.CURdiff = class_CURdiff
        desired_course.CURwork = class_CURwork
        db.session.commit()
        return success_response(desired_course.serialize())
    return failure_response("Class not found")


@app.route("/api/courses/search/<search_query>/")
def search_data(search_query):
    courses = [c.short_serialize() for c in Course.query.filter(
        or_(
            func.lower(Course.desc).contains(func.lower(search_query)),
            func.lower(Course.name).contains(func.lower(search_query))
        )
    )]
    if len(courses) == 0:
        return failure_response('No results found', 404)
    return success_response(courses)


@app.route("/api/test/success/")
def test_success():
    return success_response(None)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
