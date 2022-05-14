import requests
import os
import csv
import config

def filter_jobs(job_data, keyword, projectLength, unspecifiedJobs, hourlyRateMin, hourlyRateMax, paymentVerified, paymentUnverified, jobType, countries, create_file=True):
    if len(job_data) == 0:
        return 404

    file_header = job_data[0].keys()
    job_data_length = len(job_data)
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