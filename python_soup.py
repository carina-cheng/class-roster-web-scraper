import urllib2
from bs4 import BeautifulSoup
import json
import datetime

# Returns an array of json objects
def getSubjectJson(subjectUrl):
    # test with 'https://classes.cornell.edu/browse/roster/FA18/subject/CS'
    page = urllib2.urlopen('https://classes.cornell.edu/browse/roster/FA18/subject/CS')
    soup = BeautifulSoup(page, 'html.parser')

    #title-subjectcode
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

def response():
    status = "success"
    try:
        data = getSubjectJson('https://classes.cornell.edu/browse/roster/FA18/subject/CS')
    except:
        data = []
        status = "failed"
    
    response = {}

    response['status'] = status
    response['data'] = data
    response['date_created'] = datetime.datetime.now()

print(response())