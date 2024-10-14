About
======
This Project started as an Idea of Combining the Challonge API and Google Sheets API to reduce the manual data entry required for Google sheets and automatically update them when a Challonge board is updated.

Currently the application is pretty basic in functionality and doesn't look very appealing, but it can hook up to the Challonge V1 API and Get all the needed data and parse it in to Google Sheets.
But you can also create and manage tournaments from the application. By being able to update match data from the app, google sheets will update in real time allowing for real time updates on a leaderboard.

The plan is to implement functionality to create and manage a Main board like a Global Leaderboard or Regional one, but currently that requires all player names to be the exaact same across each sheet, which
isn't always the case. This is something I am looking in to and working with folk to get some ideas going. Application is continuly being worked on and I've been testing it at local Events and using it create quick
spreadsheets for local tournaments

This application is still in it's early days and will be changed over time. 

Running from Source
======

If you are running from the source, there are a couple of extra bits that need to be configured.

Prequisites
------

Python 3 is required to run this application.

You will need to create a Google Cloud application and setup the Credentials, OAUTH to create the credential files for runnign the application. This is to allow the connection to Google Sheets - https://console.cloud.google.com/

You will need a Challonge.com account and get the API Key from the Settings page. It is under Developer Settings

Finally you will need to have a Google SHeet created and then save the ID to the configuration via the app. https://docs.google.com/spreadsheets/d/{**SHEET_ID_IS_HERE**}/edit?gid=0#gid=0




