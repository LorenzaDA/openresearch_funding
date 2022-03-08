##################
# 1. Run scripts to scrape and get output for database
##################
# from functions in 0.grants_collection.py, we get the info for the database

# import functions

import scraper.grants_collection


# runs functions for collecting data

scraper.grants_collection.download_nih()
scraper.grants_collection.sort_text_nih()
scraper.grants_collection.ukri()


# puts data together

scraper.grants_collection.combine_funders()
