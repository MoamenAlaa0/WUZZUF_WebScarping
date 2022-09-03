from requests_html import HTMLSession
import time
import pandas as pd

# Creating session object
session = HTMLSession()

# Creating a list of dictionaries to store the data
jobs = []

def request(url):
    # Get request to the webpage
    response = session.get(url)
    # Rendering HTML
    # sleeping 3 seconds after initial render, after initial render &  Waiting before loading the page to preventing timeouts
    response.html.render(sleep=3, timeout=50000)
    # Getting links of the jobs webpages
    anchors = response.html.find('h2 > a')
    # .absolute_links returns a set object so I convert it to string
    job_links = [str(anchore.absolute_links).strip("{}'") for anchore in anchors]
    
    return job_links

def parsing(url):
    # Opening job webpage
    response = session.get(url)
    response.html.render(sleep=3, timeout=50000)
        
    try:
        Title = response.html.find('h1', first=True).text
        Job_Type = response.html.find('div.css-11rcwxl', first=True).text
        Company = response.html.find('strong', first=True).text.split('-')[0].strip()
        Area = response.html.find('strong', first=True).text.split('-')[1].split(',')[0]
        City = response.html.find('strong', first=True).text.split('-')[1].split(',')[1]
        Experience = response.html.find('span.css-4xky9y')[0].text
        Career_Level = response.html.find('span.css-4xky9y')[1].text
        Education_Level = response.html.find('span.css-4xky9y')[2].text
            
        # Setting Salary last value because there is other job details appears before it in some jobs.. like Genders
        Salary = response.html.find('span.css-4xky9y')[-1].text
            
        # Getting job categories and join all in one string
        categories = response.html.find('li.css-tmajg1')
        list_of_categs = [category.text for category in categories]
        Job_Categories = " | ".join(list_of_categs)
            
        # Same for skills and tools
        skills = response.html.find('span.css-tt12j1.e12tgh591 > span.css-158icaa')
        list_of_skills = [skill.text for skill in skills]
        Skills_and_Tools = " | ".join(list_of_skills)
            
        # Getting job description and spliting between the points by '|'
        description = response.html.find('div.css-1uobp1k > ul > li')
        list_of_descs = [point.text.strip(" .") for point in description]
        Job_Description = " | ".join(list_of_descs)
        
        # Same for job requirements
        requirements = response.html.find('div.css-1t5f0fr > ul > li')
        list_of_reqs = [point.text.strip(" .") for point in requirements]
        Job_Requirements = " | ".join(list_of_reqs)

    except: return
        
    # Saving the data
    data = {'Title': Title, 'Job_Type': Job_Type, 'Company': Company, 'Area': Area, 
            'City': City, 'Experience': Experience, 'Career_Level': Career_Level, 
            'Education_Level': Education_Level, 'Salary': Salary, 
            'Job_Categories':Job_Categories, 'Skills_and_Tools': Skills_and_Tools,
            'Job_Description': Job_Description, 'Job_Requirements':Job_Requirements}
        
    jobs.append(data)

def num_of_pages(url):
    response = session.get(url)
    response.html.render(sleep=3, timeout=50000)
    # Getting number of the pages by get # of all jobs and divide it by 15 (# of the jobs in one page)
    page_num = (int(response.html.find('strong', first=True).text) // 15)  + 1
    return page_num

def crawler(job_title):
    # Getting number of main pages
    url = f"https://wuzzuf.net/search/jobs/?a=navbg&filters%5Bcountry%5D%5B0%5D=Egypt&q={job_title}&start=0"
    page_num = num_of_pages(url)
    
    # Pagination
    for page in range(0, page_num):
        url = f"https://wuzzuf.net/search/jobs/?a=navbg&filters%5Bcountry%5D%5B0%5D=Egypt&q={job_title}&start={page}"
        
        # Returning links of all jobs webpages, 15 links per one page
        jobs_links = request(url)
        print('URL #{}: {}'.format(page+1, url))
        
        # Scraping the data from each job webpage
        for link in jobs_links:
            parsing(link)
        
        print("All is Done :)")
        time.sleep(1)

def saving_csv(list_of_dics, file_name):
    # Saving the data as CSV file using pandas library
    Data = pd.DataFrame(list_of_dics)
    Data.to_csv(file_name, index=False)

# I will scrape Data Analyst jobs (you can put any job you need, put split between the words by '-')
job_title = 'Data-Analyst'

crawler(job_title)
saving_csv(jobs, 'WUZZUF_WebScarping.csv')
