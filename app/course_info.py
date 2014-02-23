
LECTURE = 'LEC'
SEMINAR = 'SEM'
PROJECT = 'PRJ'
WORKSHOP = 'WKS'
LAB = 'LAB'
UNKNOWN = 'UNK'
COURSE_TYPES = (
    (LECTURE, 'Lecture'),
    (SEMINAR, 'Seminar'),
    (PROJECT, 'Project'),
    (WORKSHOP, 'APS Workshop'),
    (LAB, 'Lab'),
    (UNKNOWN, 'Unknown')
)

OVERALL_R = 'ALL'
WORKLOAD_R = 'WKL'
DIFFICULTY_R = 'DIF'
PROFESSOR_R = 'PRF'
RATING_TYPES = (
    (OVERALL_R, 'Overall'),
    (WORKLOAD_R, 'Workload'),
    (DIFFICULTY_R, 'Difficulty'),
    (PROFESSOR_R, 'Professor')
)

CREDIT_TYPES = [0.1, 0.15, 0.2, 0.3, 1.1, 2.5, 3.0, 3.75, 5.0, 7.5, 10.0, 12.0, 15.0, 30.0]
MAJOR_TYPES = [
('EECS', 'Electrical Engineering and Computer Science', 'SES'),
('Life', 'Life Sciences', 'SES'),
('Logistics', 'Logistics', 'SES'),
('Math', 'Mathematical Sciences', 'SES'),
('NatEnv', 'Natural and Environmental Sciences', 'SES'),
('Econ', 'Economics and Management', 'SHSS'),
('History', 'History', 'SHSS'),
('Humanities', 'Humanities', 'SHSS'),
('Law', 'Law', 'SHSS'),
('Psych', 'Psychology', 'SHSS'),
('Social', 'Social Sciences', 'SHSS'),
('Stats', 'Statistics and Methods', 'SHSS'),
('USC', 'University Studies Courses', 'USC'),
('German', 'German', 'Lang'),
('French', 'French', 'Lang'),
('Chinese', 'Chinese', 'Lang'),
('Spanish', 'Spanish', 'Lang'),
('FY', 'Foundation Year', 'FY')]