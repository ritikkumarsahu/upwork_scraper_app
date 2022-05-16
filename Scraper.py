import requests
import os
import csv
import config

def filter_jobs(job_data, keyword, projectLength, unspecifiedJobs, hourlyRateMin, hourlyRateMax, paymentVerified, paymentUnverified, jobType, countries, create_file=True):
    job_data = list(job_data)
    job_data_length = len(job_data)
    if len(job_data) == 0:
        return 404

    file_header = job_data[0].keys()
    projectLength_map = {1: projectLength['zero'], 2: projectLength['short'], 3: projectLength['medium'], 4: projectLength['long']}
    jobType_map = {1: jobType['entry'], 2: jobType['intermediate'], 3: jobType['expert']}
    
    i = 0
    count = 0
    while count < job_data_length:
        count += 1
        if (
            (projectLength_map[job_data[i]['project_length']])  and
            (not job_data[i]['is_job_fixed'] and 
                (
                    (job_data[i]['hourly_budget_min'] and job_data[i]['hourly_budget_max']) and
                    (hourlyRateMin<=job_data[i]['hourly_budget_min'] and hourlyRateMax<=job_data[i]['hourly_budget_max'])
                )
                or (unspecifiedJobs and not (job_data[i]['hourly_budget_min'] and job_data[i]['hourly_budget_max']))
            ) and
            (jobType_map[job_data[i]['job_level']]) and
            (not job_data[i]['country'] in countries) and
            (not(paymentVerified ^ paymentUnverified) or ((paymentVerified and job_data[i]['is_payment_verified']) or (paymentUnverified and not job_data[i]['is_payment_verified'])))
        ):
            i += 1
            continue

        # remove that job from job_data
        del job_data[i] 

    if create_file:
        project_lenght_map = {
            1: 'less than a month', 2: '1 to 3 months', 3: '3 to 6 months', 4: 'More than 6 months'
        }
        job_level_map = {
            1: 'beginner', 2: 'intermediate', 3: 'expert'
        }
        for i,_ in enumerate(job_data):
            job_data[i]['is_job_fixed'] = 'fixed' if job_data[i]['is_job_fixed'] else 'hourly'
            job_data[i]['is_payment_verified'] = 'verified' if job_data[i]['is_payment_verified'] else 'unverified'
            job_data[i]['job_level'] = job_level_map[job_data[i]['job_level']]
            job_data[i]['project_length'] = project_lenght_map[job_data[i]['project_length']]

        with open(os.path.join("static",f'data/{keyword}.csv'), 'w', newline='', encoding="utf-8") as csvfile:
            csv_writer = csv.DictWriter(csvfile, file_header)
            csv_writer.writeheader()
            csv_writer.writerows(job_data)
    return 200

def scrape_jobs(keyword, client_spent, last_posted, countries):
    url = config.BACKEND_BASE_URL
    params = {
        "keyword": keyword,
        "client_spent": client_spent,
        "last_posted": last_posted,
        "countries":countries
    }
    response = requests.get(url, params=params)
    print(response.url)
    return response.json()