import os
import time
import pickle
import datetime


class Schedule(object):
    courses_default = {'English': [], 'Math': [], 'Physics': [],
                       'Chemistry': [], 'Biology': [], 'History': [], 'Geography': []}
    courses_names_default = ['English', 'Math', 'Physics', 'Chemistry',
                             'Biology', 'History', 'Geography']
    today_work = {}

    def __init__(self):
        self.courses = Schedule.courses_default.copy()
        self.courses_names = Schedule.courses_names_default[::]

    def add_new_topic(self):
        print('Your Courses:')
        for i, course in enumerate(self.courses_names):
            print('    ' + str(i + 1) + '- ' + course)
        ans = input('Do you want to add a new course? (Type y for Yes, Type n): ').lower()
        while not (ans == 'y' or ans == 'n'):
            ans = input('Please enter a valid key (Type y for Yes, Type n): ').lower()
        if ans == 'y':
            self.add_new_course()

        if self.courses_names:
            print('Your Courses:')
            for i, course in enumerate(self.courses_names):
                print('    ' + str(i + 1) + '- ' + course)
            try:
                op = int(input('Choose a course from above. Enter a number (1-' +
                               str(len(self.courses_names)) + '): '))
            except ValueError:
                op = None
            while op not in range(1, len(self.courses_names) + 1):
                try:
                    op = int(input('Please enter a valid number (1-' +
                                   str(len(self.courses_names)) + '): '))
                except ValueError:
                    op = None

            course = self.courses_names[op - 1]
            print('Things you learned in', course)
            if len(self.courses[course]) == 0:
                print('    You have no entry yet.')
            else:
                for i, topic in enumerate(self.courses[course]):
                    print('    ' + str(i + 1) + '- ' + str(topic))
            topic_description = input('Write down the topic or what you learned today: ')
            self.courses[course].append(Topic(topic_description))
        else:
            print('    You do not have any courses, please add a new course before you record what you learned today.')

    def add_new_course(self):
        if len(self.courses_names) == 0:
            print('    You have no courses yet.')
        else:
            print('Your Courses:')
            for i, course in enumerate(self.courses_names):
                print('    ' + str(i + 1) + '- ' + course)
        name = input('Enter the name of the course: ').title()
        if name in self.courses.keys():
            return
        self.courses[name] = []
        self.courses_names.append(name)

    def remove_topic(self):
        if self.courses_names:
            print('Your Courses:')
            for i, course in enumerate(self.courses_names):
                print('    ' + str(i + 1) + '- ' + course)
            try:
                op = int(input('Which course does the topic you want to remove belong to? Enter a number (1-' +
                               str(len(self.courses_names)) + '): '))
            except ValueError:
                op = 0
            while op not in range(1, len(self.courses_names) + 1):
                try:
                    op = int(input('Please enter a valid number (1-' +
                                   str(len(self.courses_names)) + '): '))
                except ValueError:
                    op = 0

            course = self.courses_names[op - 1]
            if self.courses[course]:
                for i, topic in enumerate(self.courses[course]):
                    print('    ' + str(i + 1) + '- ' + str(topic))
                try:
                    op = int(input('Which topic do you want to remove? Enter a number (1-' +
                                   str(len(self.courses[course])) + '): '))
                except ValueError:
                    op = 0
                while op not in range(1, len(self.courses[course]) + 1):
                    try:
                        op = int(input('Please enter a valid number (1-' +
                                       str(len(self.courses[course])) + '): '))
                    except ValueError:
                        op = 0
                del self.courses[course][op - 1]
            else:
                print('    You haven\'t learned anything in ' + course + ' so you cannot remove anything')
        else:
            print('    You do not have any courses therefore you cannot complete this action.')

    def remove_course(self):
        if self.courses_names:
            print('Your Courses:')
            for i, course in enumerate(self.courses_names):
                print('    ' + str(i + 1) + '- ' + course)
            try:
                op = int(input('Which course do you want to remove? Enter a number (1-' +
                               str(len(self.courses_names)) + '): '))
            except ValueError:
                op = 0
            while op not in range(1, len(self.courses_names) + 1):
                try:
                    op = int(input('Please enter a valid number (1-' +
                                   str(len(self.courses_names)) + '): '))
                except ValueError:
                    op = 0
            del self.courses[self.courses_names[op - 1]]
            del self.courses_names[op - 1]
        else:
            print('    You do not have any courses that you can remove.')

    def go_back_to_default_settings(self):
        ans = input('This action can\'t be undone, Are you sure you want to do it? (Type y for Yes, Type n): ').lower()
        while not (ans == 'y' or ans == 'n'):
            ans = input('Please enter a valid key (Type y for Yes, Type n): ').lower()
        if ans == 'y':
            self.courses = Schedule.courses_default.copy()
            self.courses_names = Schedule.courses_names_default[::]

    def update_topics(self):
        print('''    Press f if you finished studying the particular topic today.
    Press d if you couldn't study the relevant topic that you were supposed to do and delay it until tomorrow.
    Press w if you haven't studied the particular topic yet but will study sometime today.''')
        if any(course for course in Schedule.today_work.keys()):
            for course in Schedule.today_work.keys():
                temp = []
                for i in range(len(Schedule.today_work[course])):
                    topic = Schedule.today_work[course][i]
                    ans = input(course + '-' + str(topic) + '(Press f, d or w): ').lower()
                    while not (ans == 'f' or ans == 'd' or ans == 'w'):
                        ans = input('Please enter a valid key (Press f, d or w): ').lower()
                    if ans == 'f':
                        topic.find_next_recap_date()
                    elif ans == 'd':
                        topic.delay_until_tomorrow()
                    if ans != 'w':
                        temp.append(topic)
                for topic in temp:
                    Schedule.today_work[course].remove(topic)
        else:
            print('There is nothing to study.')

    def display_today_schedule(self):
        print('Today\'s Study/Recap Schedule - What to do')
        key = False
        for course in self.courses_names:
            c = 1
            key2 = False
            Schedule.today_work[course] = []
            for topic in self.courses[course]:
                if topic.next_recap_date < datetime.date.today():
                    topic.next_recap_date = datetime.date.today()
                if topic.next_recap_date == datetime.date.today():
                    print('    ' + str(c) + '- ' + course + '-' + str(topic))
                    if topic not in Schedule.today_work[course]:
                        Schedule.today_work[course].append(topic)
                    c += 1
                    key = key2 = True
            if key2:
                if course != self.courses_names[-1]:
                    print('----------------')
            else:
                del Schedule.today_work[course]
        if not key:
            print('    Hurray!.. Nothing to study for today!')

    def display_courses(self):
        if self.courses_names:
            print('Your Courses:')
            for i, course in enumerate(self.courses_names):
                print('    ' + str(i + 1) + '- ' + course)
        else:
            print('    You do not have any courses.')

    def display_topics(self):
        if self.courses_names:
            print('Your Courses:')
            for i, course in enumerate(self.courses_names):
                print('    ' + str(i + 1) + '- ' + course)
            try:
                op = int(input('Which course do you want to display the topics of? Enter a number (1-' +
                               str(len(self.courses_names)) + '): '))
            except ValueError:
                op = None
            while op not in range(1, len(self.courses_names) + 1):
                try:
                    op = int(input('Please enter a valid number (1-' +
                                   str(len(self.courses_names)) + '): '))
                except ValueError:
                    op = None

            course = self.courses_names[op - 1]
            print('Things you learned in', course)
            if len(self.courses[course]) == 0:
                print('    You have no entry yet.')
            else:
                for i, topic in enumerate(self.courses[course]):
                    print('    ' + str(i + 1) + '- ' + str(topic), topic.next_recap_date)
        else:
            print('    You do not have any courses or topics.')


class Topic(object):
    def __init__(self, description):
        self.description = description
        self.next_recap_date = datetime.date.today()
        self.days = 0

    def __str__(self):
        return self.description

    def find_next_recap_date(self):
        self.days += 1
        self.next_recap_date += datetime.timedelta(days=self.days)

    def delay_until_tomorrow(self):
        self.next_recap_date += datetime.timedelta(days=1)


def main_page_prompt_user():
    print('''    1- Add a new topic.
    2- Add a new course.
    3- Remove a topic.
    4- Remove a course.
    5- Erase all the data and go back to default settings.
    6- Display today's study/recap schedule.
    7- Record what you have studied or haven't studied yet of today's schedule.
    8- Display a list of your courses.
    9- Display a list of your topics.
    10- Exit.''')
    try:
        op = int(input('What do you want to do? Enter a number (1-10): '))
    except ValueError:
        op = 0
    while op not in range(1, 11):
        try:
            op = int(input('Please enter a valid number (1-10): '))
        except ValueError:
            op = 0
    print('--------------------')
    if op == 1:
        schedule.add_new_topic()
    elif op == 2:
        schedule.add_new_course()
    elif op == 3:
        schedule.remove_topic()
    elif op == 4:
        schedule.remove_course()
    elif op == 5:
        schedule.go_back_to_default_settings()
    elif op == 6:
        schedule.display_today_schedule()
    elif op == 7:
        schedule.update_topics()
    elif op == 8:
        schedule.display_courses()
    elif op == 9:
        schedule.display_topics()
    else:
        return -1


if os.path.exists('datafile.txt') and os.stat('datafile.txt').st_size != 0:
    with open('datafile.txt', 'rb') as fh:
        schedule = pickle.load(fh)
else:
    schedule = Schedule()
x = input('Have you learned anything new today? (Type y for Yes, Type n): ').lower()
while not (x == 'y' or x == 'n'):
    x = input('Please enter a valid key (Type y for Yes, Type n): ').lower()
if x == 'y':
    schedule.add_new_topic()
    print('--------------------')
    time.sleep(1)
schedule.display_today_schedule()
print('--------------------')
time.sleep(1)
while main_page_prompt_user() != -1:
    with open('datafile.txt', 'wb') as fh:
        pickle.dump(schedule, fh)
    print('--------------------')
    time.sleep(1)
