# Brightwheel to FSAFeds Downloader/Uploader

A python script to download daycare receipts and submit them for Dependent Care reimbursement.

## Background

In order to receive reimbursement through my FSA Dependent Care Account, I have to supply daycare receipts and complete a form.

Downloading receipts from brightwheel (day care provider) requires way too many clicks and presses of the back button.  All the while, its really easy to forget what receipts you have and haven't downloaded.  Then, once you get through all that, its even more painful to upload these to FSA feds because you have to upload them manually.  

This code is a first stab at automating the process.  I need to go a step further and parse the PDF for what I paid, so I can automate the submission of how much I paid for the receipts.  AI got me this far, we can work together to get this over the finish line too. 

## Setup

cmd
pip install selenium requests beautifulsoup4 pandas

cmd
set BRIGHTWHEEL_USERNAME=your_email
set BRIGHTWHEEL_PASSWORD=your_password
set FSAFEDS_USERNAME=your_username
set FSAFEDS_PASSWORD=your_password


Update ChromeDriver Path: Replace CHROMEDRIVER_PATH with the path to your ChromeDriver executable.

Line


