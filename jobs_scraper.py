from jobspy import scrape_jobs


# full docs here: https://github.com/Bunsly/JobSpy


def scrape_all_jobs(search_term, location, hours_old, results_wanted, offset=0):
    return scrape_jobs(
        site_name=["indeed", "linkedin", "zip_recruiter", "glassdoor"],
        # site_name=["glassdoor"],
        # site_name=["linkedin"],
        search_term=search_term,
        location=location,
        distance=25,
        results_wanted=results_wanted,
        offset=offset,
        hours_old=hours_old,  # (only Linkedin/Indeed is hour specific, others round up to days old)
        # country_indeed='Israel',  # only needed for indeed / glassdoor
        linkedin_fetch_description=True,
        # proxies=["158.160.63.194:8090","93.177.67.178:80","localhost"]
    )
