# Anubriya Baskaran
# Harvard Artifacts

import pandas as pd
import requests
import sqlite3
import streamlit as st
import time

api_key = "e7b0e43d-c101-4312-87b4-36bfec652dfe"

# Streamlit Page Setup
st.set_page_config(page_title="Harvard Artifacts Explorer", layout="wide")
st.title("🏛 Harvard Artifacts Explorer")
st.markdown("Explore Harvard Artifacts by classification, save to database, and run queries.")

# Fetch Classifications

with st.spinner(" 📡 Fetching classifications from Harvard API..."):
    data_class = []
for i in range(1,8):
    data = requests.get("https://api.harvardartmuseums.org/classification",
                             {"apikey": api_key,"page":i})
    data = data.json()['records']
    data_class.extend(data)

# Creating a Dataframe of data_class
df_classification = pd.DataFrame(data_class)

# Selecting the required classifications whose objectcount >= 2500 
df_selected = df_classification[df_classification["objectcount"]>=2500]

# taking the names separately
names = df_selected['name'].tolist()

# shows valid classifications
st.success(f"✅ Found {len(names)} classifications with ≥ 2500 objects")
st.dataframe(df_selected[["name", "objectcount"]])

# User Chooses Classification

classification_choice = st.selectbox("🎨 Choose a classification", names)

#Fetch Objects for Selection

if st.button("📥 Fetch Objects"):
    st.info(f"Fetching ~2500 objects for **{classification_choice}**...")
    final_data = []
    progress = st.progress(0)

    for page in range(1, 26):  # 25 pages × 100
        data_target = requests.get("https://api.harvardartmuseums.org/object",
                                   {"apikey": api_key,
                                    "page": page, "size": 100,
                                    "classification": classification_choice})
        final_data.extend(data_target.json()['records'])

        progress.progress(int((page / 25) * 100))
        time.sleep(0.05)

    df_final = pd.DataFrame(final_data)
    st.success(f"✅ Collected {df_final.shape[0]} records for {classification_choice}")
    st.dataframe(df_final.head(10))

    st.session_state['df_final'] = df_final  # save in session_state

    # continue with fetched data
    if 'df_final' in st.session_state:
        df_final = st.session_state['df_final']


        # Split into Tables

        # metadata dataframe
        df_metadata = df_final[[
            "id", "title", "culture", "period", "century",
            "medium", "dimensions", "description", "department",
            "classification", "accessionyear", "accessionmethod"
        ]]


        # media dataframe
        df_media = df_final[[
            "id", "imagecount", "mediacount", "colorcount",
            "rank", "datebegin", "dateend"
        ]].rename(columns={"id": "objectid"})


        # colors dataframe
        color_records = []
        for _, row in df_final.iterrows():   
            colors = row.get("colors")       # get the "colors" field of this artifact
            if isinstance(colors, list):     # only if it's a list and if color exist
                for c in colors:             
                    color_records.append({   
                        "objectid": row["id"],       
                        "color": c.get("color"),     
                        "spectrum": c.get("spectrum"),
                        "hue": c.get("hue"),
                        "percent": c.get("percent"),
                        "css3": c.get("css3")
                    })

        df_colors = pd.DataFrame(color_records)

        st.session_state['df_metadata'] = df_metadata
        st.session_state['df_media'] = df_media
        st.session_state['df_colors'] = df_colors


        # Show Tables

        st.subheader("📊 View Data Tables")
        tab1, tab2, tab3 = st.tabs(["Metadata", "Media", "Colors"])
        tab1.dataframe(df_metadata.head(20))
        tab2.dataframe(df_media.head(20))
        tab3.dataframe(df_colors.head(20))

# Insert into Database

if 'df_final' in st.session_state:
    if st.button("💾 Insert into Database"):

    

        conn = sqlite3.connect("harvard_artifacts.db")
        cursor = conn.cursor()

        
        # check if classification already exists

        cursor.execute("SELECT COUNT(*) FROM artifact_metadata WHERE classification=?", (classification_choice,))

        already_inserted = cursor.fetchone()[0] > 0 # check if any rows exist


        if already_inserted:
            st.warning(f"⚠️ '{classification_choice}' is already inserted in DB.")
        else:
            df_metadata.to_sql("artifact_metadata", conn, if_exists="append", index=False)
            df_media.to_sql("artifact_media", conn, if_exists="append", index=False)
            df_colors.to_sql("artifact_colors", conn, if_exists="append", index=False)
            st.success(f"✅ Inserted {classification_choice} into database successfully.")

        conn.close()


# Define Queries

st.title("🔍 Harvard Artifacts SQL Query Explorer")
st.markdown("Select a query from the dropdown to execute it and see results.")

# Connect to DB
conn = sqlite3.connect("harvard_artifacts.db")
cursor = conn.cursor()

# Define Queries
queries = {
    "🏺 Metadata: 1. List all artifacts from the 11th century belonging to Byzantine culture":
        "SELECT * FROM artifact_metadata WHERE century LIKE '%11%' AND culture LIKE '%Byzantine%';",

    "🏺 Metadata: 2. Unique cultures represented in the artifacts":
        "SELECT DISTINCT culture FROM artifact_metadata WHERE culture IS NOT NULL;",

    "🏺 Metadata: 3. List all artifacts from the Archaic Period":
        "SELECT * FROM artifact_metadata WHERE period LIKE '%Archaic%';",

    "🏺 Metadata: 4. Artifact titles ordered by accession year descending":
        "SELECT title, accessionyear FROM artifact_metadata WHERE accessionyear IS NOT NULL ORDER BY accessionyear DESC;",

    "🏺 Metadata: 5. Number of artifacts per department":
        "SELECT department, COUNT(*) AS artifact_count FROM artifact_metadata WHERE department IS NOT NULL GROUP BY department;",

    "🖼 Media: 6. Artifacts with more than 1 image":
        "SELECT * FROM artifact_media WHERE imagecount > 1;",

    "🖼 Media: 7. Average rank of all artifacts":
        "SELECT AVG(rank) as avg_rank FROM artifact_media WHERE rank IS NOT NULL AND rank > 0;",

    "🖼 Media: 8. Artifacts where colorcount > mediacount":
        "SELECT * FROM artifact_media WHERE colorcount > mediacount;",

    "🖼 Media: 9. Artifacts created between 1500 and 1600":
        "SELECT * FROM artifact_media WHERE datebegin >= 1500 AND dateend <= 1600;", 

    "🖼 Media: 10. Number of artifacts with no media files":
        "SELECT COUNT(*) as no_media_count FROM artifact_media WHERE mediacount = 0 OR mediacount IS NULL;",

    "🎨 Colors: 11. Distinct hues used":
        "SELECT DISTINCT hue FROM artifact_colors WHERE hue IS NOT NULL;",

    "🎨 Colors: 12. Top 5 most used colors by frequency":
        "SELECT color, COUNT(*) AS freq FROM artifact_colors GROUP BY color ORDER BY freq DESC LIMIT 5;", 

    "🎨 Colors: 13. Average coverage percentage per hue":
        "SELECT hue, AVG(percent) AS avg_percent FROM artifact_colors WHERE hue IS NOT NULL GROUP BY hue;", 

    "🎨 Colors: 14. Colors used for the first artifact":
        "SELECT * FROM artifact_colors WHERE objectid = (SELECT MIN(id) FROM artifact_metadata);",

    "🎨 Colors: 15. Total number of color entries":
        "SELECT COUNT(*) as total_colors FROM artifact_colors;",

    "🔗 Join: 16. Titles and hues for artifacts belonging to Byzantine culture":
        "SELECT m.title, c.hue FROM artifact_metadata m JOIN artifact_colors c ON m.id=c.objectid WHERE m.culture LIKE '%Byzantine%';",

    "🔗 Join: 17. Each artifact title with associated hues":
        "SELECT m.title, c.hue FROM artifact_metadata m JOIN artifact_colors c ON m.id=c.objectid ORDER BY m.title;", 

    "🔗 Join: 18. Artifact titles, cultures, and media ranks where period is not null":
        "SELECT m.title, m.culture, me.rank FROM artifact_metadata m JOIN artifact_media me ON m.id=me.objectid WHERE m.period IS NOT NULL;", 

    "🔗 Join: 19. Artifact titles in top 10 rank including hue 'Grey'":
        "SELECT m.title, me.rank, c.hue FROM artifact_metadata m JOIN artifact_media me ON m.id=me.objectid JOIN artifact_colors c ON m.id=c.objectid WHERE c.hue='Grey' ORDER BY me.rank ASC LIMIT 10;",

    "🔗 Join: 20. Artifacts per classification and average media count":
        "SELECT m.classification, COUNT(*) AS artifact_count, AVG(me.mediacount) AS avg_media FROM artifact_metadata m JOIN artifact_media me ON m.id=me.objectid GROUP BY m.classification ORDER BY artifact_count DESC;", 

    # DIY Simple Queries (10 examples)
    "DIY 1. Artifacts with medium containing 'Gold'":
        "SELECT * FROM artifact_metadata WHERE medium LIKE '%Gold%';",

    "DIY 2. Artifacts from culture 'Egyptian'":
        "SELECT * FROM artifact_metadata WHERE culture LIKE '%Egyptian%';",

    "DIY 3. Artifacts with more than 2 colors":
        "SELECT objectid, COUNT(*) as color_count FROM artifact_colors GROUP BY objectid HAVING COUNT(*) > 2;",

    "DIY 4. Count of artifacts per century":
        "SELECT century, COUNT(*) AS artifact_count FROM artifact_metadata GROUP BY century;", 

    "DIY 5. Artifacts with no description":
        "SELECT * FROM artifact_metadata WHERE description IS NULL OR description='';", 

    "DIY 6. Media with colorcount = 0":
        "SELECT * FROM artifact_media WHERE colorcount = 0;", 

    "DIY 7. Top 5 artifacts with highest mediacount":
        "SELECT * FROM artifact_media ORDER BY mediacount DESC LIMIT 5;", 

    "DIY 8. Dominant color per artifact (highest coverage %)":
        "SELECT objectid, color, hue, MAX(percent) AS max_percent FROM artifact_colors GROUP BY objectid;",

    "DIY 9. Artifacts with 'Vase' in title":
        "SELECT * FROM artifact_metadata WHERE title LIKE '%Vase%';", 

    "DIY 10. Average color percent per color":
        "SELECT color, AVG(percent) AS avg_percent FROM artifact_colors GROUP BY color;"
}


# Dropdown for queries
query_choice = st.selectbox("Select a SQL query to execute", list(queries.keys()))

if st.button("Execute Query"):
    sql = queries[query_choice]
    try:
        df_result = pd.read_sql_query(sql, conn)
        st.success(f"✅ Query executed successfully. {len(df_result)} rows fetched.")
        st.dataframe(df_result)
    except Exception as e:
        st.error(f"❌ Error executing query: {e}")

# Close connection
conn.close()
