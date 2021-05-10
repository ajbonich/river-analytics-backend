This repo is a backend RESTful API for riverflowcast.com.

Function:
Daily data is retrieved from USGS endpoints.
This data is used to compute the average seasonal flow for a given USGS site.
The data is also used to create forecasts for the rest of the calendar year.


Future Ideas:

    Seasonal Stats:
    - Calendar of kayak runs and when they run - when to do what run when in the spring runoff
        - average date of peak for each run
            - deviation analysis of peak (cfs variance and date variance)
                - compare different runs to determine trends
                - is there a "normal" for different historic time periods (after a dam was built?)
        - Average of daily maxes for every day


    Compare peak runoff/length of runable season to:
        - Snow water equivalent 
        - average temperature


    Daily Look-up:
    - Average historic flow for a specific day 
        - percentile compared to median
    - daily min/max swings
        - time of day these happen?

    Trip Planning:
    - Average runnable period
