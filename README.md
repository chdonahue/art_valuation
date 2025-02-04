# Art Valuation Project

### To install on Mac:

    1. python3.12 -m venv venv
    2. source venv/bin/activate
    3. pip install -r requirements.txt

### To run:
1. Create /data in the root directory
2. python arnet_to_csv.py
This creates artnet_results.csv

### Notes:
This parses all the artnet pdf pages into a single .csv file (artnet_results). It still needs some cleaning within each field, but most that is left is pretty trivial. It would be best to have the variables for the ML models thought out first before putting more work into it. If I were to go further with this:

    1. The description field can be parsed separately (whether it was signed makes a big difference in value, and the misc field may not be reliable)
    2. Some entries from desription are missing. I'd figure out why. I must have missed an edge case. 
    3. Medium has important key words that should be separately extracted prior to feeding into ML (oil, canvas, linen)
    4. Lots of small cleaning to be done in some of the fields (i.e. date has single years sometimes, ranges other times)
    5. Sold for has more information besides price (i.e. Premium or not)


### Assignment:

This assignment asks you to design and build a small part of the ML pipeline that will hopefully serve as the foundation for future work on this project. 

Attached ZIP is a series of documents from Artnet, a database containing information about the sales history of various artworks. In order to build a valuation model, we’ll need to convert these documents into a format usable for model training. 

The deliverable is a program in any language/framework that will take as input a list of similarly formatted PDFs, and output a CSV file with “clean” data. By “clean” data, we mean a table in human-readable format that can subsequently be encoded using standard functions (i.e. categorical variables should use human-readable names rather than be replaced with a number). 

We are purposefully leaving the specific format of the output to you, as we'd like to learn about how you curate data and features. There is no need to make a fancy UI - running a script on the terminal is sufficient. 

We also expect that there will be multiple “correct” ways of getting to your final result. Feel free to use any external APIs or libraries as required, but please be prepared to explain all rationale behind your thought process. In our next call, we will discuss your methodology and how you might construct additional parts of the ML pipeline. 