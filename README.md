# introtodb

## Intern Hunt

Part 1.3

Name and UNI:
Siddharth Shah - sas2387
Abhijeet Mehrotra - am4586

Postgre Account: sas2387

URL:
http://146.148.87.71:8111/student/login
http://146.148.87.71:8111/recruiter/login
http://146.148.87.71:8111/company/login

We haven't made any changes to the schema we defined in the part 2 of the assignment.

We have implemented all parts proposed in Part 1.

Student, recruiter, and company can login in the portal with their respective logins with restricted roles.

Students can search for different types of job and apply for them using pdf resumes.
Students can see all their applications on the dashboard.
Students can set their education profile.
Students can set their skills profile.
Students can set their experience profile.

Recruiter can see all the jobs posted by him/her.
Recruiter can post new jobs.
Recruiter can close existing jobs.
Rectruiter can see full student profile and accept/reject applicants.


Done Extra:
Company can see all their recruiter.
Company can change the recruiter for a specific job


Most Interesting:
Student View Jobs
	Students can view different kinds of open jobs and can search for jobs based on parameters like "position", "fromdate" ,"todate", "company" and sort by various options.

	Inputs from search form are used to create the select query to get 'jobposition' and 'company' from backend and return result based on search which uses 'inner join', 'where' and 'orderby' clauses.

Recruiter View Applications:
	Recruiter can view open and closed positions, position details and application statistical data

	It gets applicant statistical information from 'jobposition' and 'application' using join. Then it displays information of open and closed positions posted by the HR and statistical application information for open positions. 


Company Dashboard
	Company can see all their hrs and jobs and modify hrs for the exisiting jobs. Company can also see number of applicants accepted, rejected, pending for a given job.

	Company can see statistic of jobs, which uses orderby clause on 'application' on 'pid' and 'status'. 


