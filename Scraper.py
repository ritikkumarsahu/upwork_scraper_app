import requests
import os
import csv
def filter_jobs(job_data, keyword, projectLength, unspecifiedJobs, hourlyRateMin, hourlyRateMax, paymentVerified, paymentUnverified, jobExpert, jobIntermediate, jobEntry, countries, create_file=True):
    if len(job_data) == 0:
        return 404
    res_data = []
    # TODO: filter the conditions here
    if create_file:
        with open(os.path.join("static",f'data/{keyword}.csv'), 'w', newline='', encoding="utf-8") as csvfile:
            csv_writer = csv.DictWriter(csvfile, job_data[0].keys())
            csv_writer.writeheader()
            csv_writer.writerows(job_data)
    return 200

def scrape_jobs(keyword, client_spent, last_posted, countries):
    url = "http://backend:3000"
    params = {
        "keyword": keyword,
        "client_spent": client_spent,
        "last_posted": last_posted,
        "countries":countries
    }
    # response = requests.get(url, params=params)
    # return response.json()
    return [params]



