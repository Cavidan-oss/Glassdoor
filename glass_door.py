import requests 
from bs4 import BeautifulSoup as bs4
import pandas as pd


header = {}

def get_soup(url, header):

    request=requests.get(url, headers = header)

    content=request.content

    soup=bs4(content, 'html.parser')
    
    return soup


def get_country_name(url):
    
    country = url.split('-')[3]
    
    return country
    

def get_job_titles(data):
    """
    Parameters
    ----------
    data : Accepts the soup element ..

    Returns
    -------
    job_names : A list contains all the job titles 
    """
    
    job_names = []
        
    for title in data:
        new_title = title.find('a')
        job_names.append(new_title.text)
    
    
    return job_names


def get_job_data(data):
    """
    Returns the median salary, job satisfaction and number of open jobs.
    """
    
    median_salary, job_satisfaction, job_openings = [], [], []

    redirect = {'Median Base Salary':median_salary, 'Job Satisfaction' :job_satisfaction,"Job Openings":job_openings, 'Career Opportunity' : job_satisfaction}
    
    for data_point in data[5:]:
        titles = ' '.join(data_point.text.split(' ')[2:])
        numeric_data = data_point.text.split(' ')[1]
        
        if titles.strip() in redirect.keys():
            redirect[titles.strip()].append(numeric_data)
        
    return median_salary, job_satisfaction, job_openings



def get_country_urls(soup):
    
    countries = soup.find('select', {'name' : 'listLocations'})

    country_url = countries.find_all('option')
    
    return [f"https:{i.get('data-url')}" for i in country_url]
    
    
def get_all_links(country_urls):
    total_urls = {}
    
    for country_url in country_urls:
        
        
        test_soup = get_soup(country_url,header)
        year_options = test_soup.find('select',{'class' : 'listArchive'})
        years = year_options.text.split(' ')[1:]
        
        selected_years = year_options.find_all('option')
        
     
        urls = {f"https://www.glassdoor.co.uk{url.get('data-url')}":(year,get_country_name(url.get('data-url'))) for url,year in zip(selected_years, years)}
        
        total_urls.update(urls)
        
    return total_urls
    

def main(origin_url, file_name, scratch = True):

    if scratch:
        with open(f'{file_name}.csv', 'w') as file:
            file.write(','.join(["Rank", "Title", "Salary", "Satisfaction", "Year", "Country"]) + '\n')
    
    base_soup = get_soup(origin_url, header)
    urls = get_country_urls(base_soup)
    all_urls = get_all_links(urls)
    
    for url in all_urls.keys():
        
        soup = get_soup(url, header)
        job_titles = soup.find_all('p', {'class' : "h2 m-0 entryWinner pb-std pb-md-0"})
        
        job_data = soup.find_all('div', {'class': 'dataPoint'})
    
        job_names = get_job_titles(job_titles)
        median_salary, job_satisfaction, job_openings = get_job_data(job_data)
        median_salary = list(map(lambda x : x.replace(',','.'),median_salary))
    
        
        for place,name, salary, satis, year, country in zip(range(1,len(job_names)+1),job_names, median_salary, job_satisfaction, [all_urls[url][0]]*len(job_names),[all_urls[url][1]]*len(job_names)):
            file = open(f"{file_name}.csv",'a')
            file.write(','.join([str(place),name, ''.join([salary]), satis, year, country])+'\n')
       
    
    file.close()


url = 'https://www.glassdoor.com/List/Best-Jobs-in-America-2016-LST_KQ0,25.htm'

main(url, 'Glassdoor_Best_Jobs')
