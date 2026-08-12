# ETL template

I created this template to make it easier for me start any data engineering project
If you find this useful, you can copy it for your own project

## Structure

Below is the basic folder structure, you may or may not need everyfile. I would suggest to use .env to
keep sensitive information like secrets and even the URL to your database, even if you are a beginner; 
it is a good security practise. ".gitkeep" are just placeholder files to ensure that empty folders are
cloned, if not git will ignore them and template structure breaks.

``` text
│   .env
│   .gitignore
│   main.py
│   README.md
│   requirements.txt
│   
├───data
│   ├───archive
│   │       .gitkeep
│   │
│   ├───processed
│   │       .gitkeep
│   │
│   └───raw
│           .gitkeep
│
├───notebooks
│       visualization.ipynb
│
├───src
│       extract_data.py
│       load_data.py
│       transform_data.py
│       __init__.py
│
└───tests
        test_extract_data.py
		test_transform_data.py
		test_load_data.py
```

