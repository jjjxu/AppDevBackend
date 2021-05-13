# backend for the fun class

this is an attempt at categorizing the large Cornell class offering and allowing the user to search for keywords.

at a summary, it is a wrapper that caches the Cornell class roster and combines it with web-scraped data from CUReviews.

note: a second table was not used because we could not figure out how to best implement it with our current needs. We spent the majority of time learning how to web-scrape, because we wanted to start off with a dataset that was already compiled and public. 

## Public API spec:

### Get details about a specific class

    GET /api/courses/<course_subject>/<course_code/>

Response:

    {
        "success": true, 
        "data":
        {
            "id": <database id>,
            "subject": <class subject>,
            "code": <class number>,
            "name": <class title>,
            "description": <class description>,
            "credit_count": <class credits>,
            "CU_Reviews_Overall": <CU Reviews Overall Rating>,
            "CU_Reviews_Difficulty": <CU Reviews Difficulty>,
            "CU_Reviews_Workload": <CU Reviews Workload>
        }

    }

### Search for tags/keywords

    GET /api/courses/search/<query>/

Response:

    {
        "success": true,
        "data":
        {
            [
                {
                    "subject": <class subject 1>, 
                    "code": <class number 1>
                }, 
                {
                    "subject": <class subject 2>, 
                    "code": <class number 2>
                }, 
                ...
            ]
        }
    }

## Private API spec:

Notes: These APIs may not function correctly because they rely on CUReviews, an external site. An update before preenroll appears to have broken the web scraping functionality. In short, CUReviews is a React website, and thus requires client-side rendering and execution of Javascript in order to produce a HTML page that's viewable. However, when automating visits and rendering the Javascript, there is a bug that was introduced last week (see the latest Github commit about a week ago, as of 12 May 2021) which breaks the rendering pipeline when non-human visitors visit the site.

### Update all classes

    POST /api/internal/update/

Important note: *This web scrape is exhaustive; takes about three hours to execute*

Expected Request:

    {
        "CONFIRM": true
    }

Response:

    {
        "success": true,
        "data": null
    }

### Update specific class

    GET /api/internal/update/

Response:

    {
        "success": true, 
        "data":
        {
            "id": <database id>,
            "subject": <class subject>,
            "code": <class number>,
            "name": <class title>,
            "description": <class description>,
            "credit_count": <class credits>,
            "CU_Reviews_Overall": <CU Reviews Overall Rating>,
            "CU_Reviews_Difficulty": <CU Reviews Difficulty>,
            "CU_Reviews_Workload": <CU Reviews Workload>
        }

    }
