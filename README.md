# Harvard-Artifacts-Explorer
This is a data-driven application built using Python, Streamlit, SQLite, and the Harvard Art Museums API. The goal of the project is to fetch, store, and explore artifact data from the Harvard Art Museums. Users can interactively choose artifact classifications, fetch objects, save the data in a database, run SQL queries to analyze the collection.  

Project Overview  
This project explores artifacts from the Harvard Art Museums API using a Streamlit web application.  
The application allows users to:  
- Fetch artifact data by classification (only those with more than 2500 objects).  
- Split and store artifact details into three structured SQLite tables:  
  - artifact_metadata (general info)  
  - artifact_media (media info)  
  - artifact_colors (color details)  
- Insert data into a local SQLite database (harvard_artifacts.db).  
- Run 30 SQL queries (20 given + 10 DIY queries) via dropdown and view results instantly.  

Tech Stack  
- Python  
- Streamlit (UI framework)  
- SQLite (database)  
- Pandas and Requests (data handling and API calls)  

Project Files  
- final.py → Main Streamlit app code  
- harvard_artifacts.db → SQLite database file (generated after inserting data)
- Project Report
- Project PPT
- Screenshots

How to Run the Project  
1. Download the Repository  
  
2. Install Required Packages  
   pip install streamlit pandas requests  

3. Run the Streamlit App  
   streamlit run final.py  

4. Interact with the Application  
   - Choose a classification  
   - Fetch artifacts (greater than or equal to 2500 objects)  
   - View metadata, media, and color tables  
   - Insert into database  
   - Select SQL queries from dropdown and view results  

SQL Query Explorer  
The app provides 30 SQL queries under categories:  
- Metadata Queries (5)  
- Media Queries (5)  
- Colors Queries (5)  
- Join Queries (5)  
- DIY Queries (10 extra queries)  

Each query can be executed with one click, and results are shown in a Streamlit dataframe.   

Author  
Anubriya Baskaran  
Data Science Enthusiast 
