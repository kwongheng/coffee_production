# Coffee Production

This is a JDE10 interim project to flex ETL muscles for the programme trainees

## Structure (to be updated)

- data folder is used for downloading and storing extracted data, the data is not kept in the repo since it can be easily generated
- main.py will be the main script that calls the ETL scripts


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

## Branches

- etl_scripts: to develop ETL related scripts


