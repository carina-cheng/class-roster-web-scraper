import urllib2
from bs4 import BeautifulSoup
import json
import datetime
import sys

def getSubjects():
    """ Returns a json list of all possible subjects in the SP18 semester
    """
    page = urllib2.urlopen('https://classes.cornell.edu/browse/roster/SP18')
    soup = BeautifulSoup(page, 'html.parser')

    subjects = soup.find_all('ul', class_ = 'subject-group')

    results = []

    for subject in subjects:
        subjectInfo = {}

        info = subject.find_all('a')
        subjectInfo['code'] = str(info[0].get_text())
        subjectInfo['name'] = str(info[1].get_text())

        results.append(subjectInfo)

    jsonData = json.dumps(results, indent=4)

    return results

def getSubjectCourses(subjectCode):
    """ Returns a json list of all possible courses in [subjectCode]
        Requires: [subjectCode] must be a valid string
    """
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

    jsonData = json.dumps(results, indent=4)

    return results

def getCourseDetails(courseUrl):
    """ Returns a dictionary of information from the 'more details' link on each course.
        Includes the course description, list of semesters available, pre/co-requisites, 
        forbidden overlaps, and distribution requirement
    """
    page = urllib2.urlopen(courseUrl)
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
    
    if catalog is None: 
        return ''

    promptLength = len(catalog.find('span', class_ = 'catalog-prompt').get_text())
    catalogValue = catalog.get_text()[promptLength+1:]

    return catalogValue

def subjectsResp():
    """ Returns the response as a json for getting all subjects with error handling
    """
    try:
        status = "success"
        data = getSubjects()
    except:
        status = "failed"
        data = []

    response = {}

    response['status'] = status
    response['data'] = data
    response['date_created'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    jsonData = json.dumps(response, indent=4)

    return jsonData

def courseResp(subjectCode):
    """ Returns the response as a json for getting courses from [subjectCode] 
        with error handling
    """
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
    response['date_created'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    jsonData = json.dumps(response, indent=4)

    return jsonData

if __name__ == "__main__":
    numArgs = len(sys.argv)-1
    if numArgs == 1 and str(sys.argv[1]) == 'help':
        helpResp = "Available Commands: \n"
        helpResp += "   [list_subjects]       Lists the codes and names of all possible subjects in that semester, no argument required \n"
        helpResp += "   [list_courses]        Lists the course details from the subject given in [args]. Available arguments/course codes found in list_subjects \n\n"
        helpResp += "To run a command, type python main.py [command_name] [args]"
        
        print(helpResp)
    elif numArgs == 1 and sys.argv[1] == 'list_subjects':
        print(subjectsResp())
    elif numArgs == 2 and sys.argv[1] == 'list_courses':
        print(courseResp(sys.argv[2]))
    else:
        firstLine = 'Invalid command. '
        if numArgs == 0:
            firstLine = 'Please insert arguments for the script. '
        elif numArgs > 2:
            firstLine = 'Too many arguments inputted. '
        print(firstLine + "Type 'python python_soup.py help' for listed commands") 