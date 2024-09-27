from jobspy import scrape_jobs


# full docs here: https://github.com/Bunsly/JobSpy


def scrape_all_jobs(site_name, search_term, location, hours_old, results_wanted, offset=0):
    site_name = [item.strip() for item in site_name.split(',')]
    return scrape_jobs(
        site_name=site_name,
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
