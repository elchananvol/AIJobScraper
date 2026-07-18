import os


# full docs here: https://github.com/Bunsly/JobSpy


def _split_csv(value):
    if value is None or value == "":
        return None
    return [item.strip() for item in str(value).split(",") if item.strip()]


def _get_bool_env(name, default=None):
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _get_int_env(name, default):
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return int(value)


def scrape_all_jobs(site_name, search_term, location, hours_old, results_wanted, offset=0):
    from jobspy import scrape_jobs

    site_name = _split_csv(site_name)
    job_types = _split_csv(os.getenv("job_type"))
    proxies = _split_csv(os.getenv("proxies"))

    kwargs = {
        "site_name": site_name,
        "search_term": search_term,
        "location": location,
        "distance": _get_int_env("distance", 25),
        "results_wanted": int(results_wanted),
        "offset": offset,
        "hours_old": int(hours_old) if hours_old not in (None, "") else None,
        "country_indeed": os.getenv("country_indeed") or None,
        "linkedin_fetch_description": _get_bool_env("linkedin_fetch_description", True),
        "description_format": os.getenv("description_format", "markdown"),
        "verbose": _get_int_env("jobspy_verbose", 1),
        "proxies": proxies,
    }

    if job_types:
        kwargs["job_type"] = job_types[0] if len(job_types) == 1 else job_types

    is_remote = _get_bool_env("is_remote")
    if is_remote is not None:
        kwargs["is_remote"] = is_remote

    easy_apply = _get_bool_env("easy_apply")
    if easy_apply is not None:
        kwargs["easy_apply"] = easy_apply

    return scrape_jobs(
        **{key: value for key, value in kwargs.items() if value is not None}
    )
