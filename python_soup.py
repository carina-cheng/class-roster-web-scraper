import urllib2
from bs4 import BeautifulSoup
import json
import datetime
import sys

def getSubjects():
    page = urllib2.urlopen('https://classes.cornell.edu/browse/roster/SP18')
    soup = BeautifulSoup(page, 'html.parser')

    subjects = soup.find_all('ul', class_ = 'subject-group')

    for subject in subjects:
        subjectInfo = {}

        info = subject.find_all('a')
        subjectInfo['code'] = str(info[0].get_text())
        subjectInfo['name'] = str(info[1].get_text())

    return 

# Returns an array of json objects
def getSubjectCourses(subjectCode):
    page = urllib2.urlopen('https://classes.cornell.edu/browse/roster/FA18/subject/' + subjectCode)
    soup = BeautifulSoup(page, 'html.parser')

    courses = soup.find_all('p', class_ = 'course-descr')

    results = []

    for course in courses:
        courseData = {}

        key = course.a['id']
        courseData['id'] = str(key[key.find('-')+1:])

        link = 'https://classes.cornell.edu' + str(course.a['href'])

        details = getCourseDetails(link)
        courseData['semesters'] = details['semesters']
        courseData['requisites'] = details['requisites']
        courseData['forbid'] = details['forbid']
        courseData['distr'] = details['distr']

        results.append(courseData)

    jsonData = json.dumps(results)

    return jsonData

def getCourseDetails(courseUrl):
    # test with 'https://classes.cornell.edu/browse/roster/FA18/class/CS/1110'
    page = urllib2.urlopen('https://classes.cornell.edu/browse/roster/FA18/class/CS/1110')
    soup = BeautifulSoup(page, 'html.parser')

    courseInfo = {}
    
    courseInfo['descr'] = soup.find('p', class_ = 'catalog-descr').get_text()

    semsAvailable = getCatalogValue(soup, 'catalog-when-offered').encode('ascii', 'ignore')
    semestersList = map(str, semsAvailable.strip('.').split(', '))
    courseInfo['semesters'] = semestersList

    courseInfo['requisites'] = getCatalogValue(soup, 'catalog-prereq').encode('ascii', 'ignore')

    courseInfo['forbid'] = getCatalogValue(soup, 'catalog-forbid').encode('ascii', 'ignore')

    courseInfo['distr'] = getCatalogValue(soup, 'catalog-distr').encode('ascii', 'ignore')

    return courseInfo

def getCatalogValue(soup, classStr):
    catalog = soup.find('span', class_ = classStr)
    promptLength = len(catalog.find('span', class_ = 'catalog-prompt').get_text())
    catalogValue = catalog.get_text()[promptLength+1:]

    return catalogValue

def courseResp(subjectCode):
    try:
        status = "success"
        data = getSubjectCourses(subjectCode)
    except:
        status = "failed"
        data = []
    
    response = {}

    response['status'] = status
    response['code'] = subjectCode
    response['data'] = data
    response['date_created'] = datetime.datetime.now()

def subjectsResp():
    try:
        status = "success"
        data = getSubjects()
    except:
        status = "failed"
        data = []

    response = {}

    response['status'] = status
    response['data'] = data
    response['date_created'] = datetime.datetime.now()
