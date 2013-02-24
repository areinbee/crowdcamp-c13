=== The directory structure of this repository ===

<experiment name>/: A directory representing an experiment, including the experimental protocol (web-app), data collected, and analysis code.
    web-app/: The web page used for gathering data for the experiment on Amazon Mechanical Turk.  All resources are copied inside, so it should be self-contained, including how to upload it to a server.
    data-and-analysis/: The directory containing data gathered from the experiment using the web-app, including instructions for creating HITs on Amazon Mechanical Turk that use the web-app.  Also includes code for analyzing the data.

ext/: External code.
attic/: Things of possible interest that have been used in the past but aren't used by any current projects.
