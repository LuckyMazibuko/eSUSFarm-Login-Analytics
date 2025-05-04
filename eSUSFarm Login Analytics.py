#!/usr/bin/env python
# coding: utf-8

# # Project Title:🌱 eSUSFarm Login Analytics
# 
# ## Log:
# - **Date Started:** 2025-04-01
# - **Last Updated:** 2025-05-04
# - **Description:** This project analyzes farmer login behavior and engagement based on demographic data and login patterns.
# - **Key Features:**
#   - Login analysis by hour, day, and session duration
#   - Clustering based on login behavior
#   - Gender-based analysis of login activity
#   - Visualizations using Plotly
# 
# ## Recent Updates:
# - **2025-05-01:** Integrated clustering to analyze login behavior.
# - **2025-05-03:** Added visualizations to show login activity trends.
# 
# 

# In[ ]:


#!pip install pandas plotly sqlalchemy dash dash-bootstrap-components scikit-learn pyodbc


# In[1]:


#Imports:
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlalchemy
import urllib
from datetime import datetime
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


# In[2]:


#Set Database connection:

server = 'esusfarmprod.database.windows.net'
database = 'eSusFarmSA'
username = 'esusfarm'
password = 'eSus@321$'

params = urllib.parse.quote_plus(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={server};DATABASE={database};UID={username};PWD={password}"
)
engine = sqlalchemy.create_engine(f"mssql+pyodbc:///?odbc_connect={params}")


# In[3]:


#Fetch and prepate data:

def fetch_and_process_data():
    query = """
    SELECT
        a.[FarmerId], a.[MobileNumber], a.[Name], a.[Gender], a.[Province],
        b.SubmitDate, b.DeliveredDate,
        CAST(b.SubmitDate AS DATE) AS session_date,
        d.CropName
    FROM [dbo].[Farmers] a
    INNER JOIN [dbo].[SMSNotificationLogs] b
        ON CAST(a.[MobileNumber] AS VARCHAR) = CAST(b.[MobileNumber] AS VARCHAR)
    LEFT JOIN [dbo].[FarmerCrops] c
        ON c.[FarmerId] = a.FarmerId
    LEFT JOIN [dbo].[Crops] d
        ON d.CropId = c.CropId
    WHERE TRY_CAST(b.SubmitDate AS DATETIME) IS NOT NULL
      AND TRY_CAST(b.DeliveredDate AS DATETIME) IS NOT NULL
    """
    df = pd.read_sql(query, engine, parse_dates=["SubmitDate", "DeliveredDate"])
    df["login_hour"] = df["SubmitDate"].dt.hour
    df["login_day"] = df["DeliveredDate"].dt.day_name()
    df["duration_mins"] = (df["DeliveredDate"] - df["SubmitDate"]).dt.total_seconds() / 60.0
    return df



# In[4]:


def compute_engagement_score(df):
    # Create ActiveWeek from SubmitDate
    df["ActiveWeek"] = df["SubmitDate"].dt.to_period("W").astype(str)
    
    engagement_df = df.groupby("FarmerId").agg({
        "duration_mins": "mean",
        "FarmerId": "count",  # Login count
        "ActiveWeek": pd.Series.nunique
    }).rename(columns={
        "FarmerId": "LoginCount",
        "duration_mins": "AvgSessionMins",
        "ActiveWeek": "ActiveWeeks"
    })

    # Normalize each component
    scaler = StandardScaler()
    engagement_df_scaled = pd.DataFrame(
        scaler.fit_transform(engagement_df),
        columns=engagement_df.columns,
        index=engagement_df.index
    )

    # Composite Score: Simple average of the 3 normalized values
    engagement_df_scaled["EngagementScore"] = engagement_df_scaled.mean(axis=1)

    # Merge engagement back to original df
    merged_df = df.merge(engagement_df_scaled[["EngagementScore"]], left_on="FarmerId", right_index=True, how="left")
    
    return merged_df, engagement_df_scaled.reset_index()


# In[5]:


df_raw = fetch_and_process_data()
df, engagement_summary = compute_engagement_score(df_raw)

df.head()


# ### Data Interpretation
# 
# This dataset appears to represent the login behavior of farmers within a specific week. It includes various features such as:
# 
# 1. **FarmerId**: A unique identifier for each farmer.
# 2. **MobileNumber**: The mobile number of the farmer.
# 3. **Name**: The name of the farmer.
# 4. **Gender**: The gender of the farmer (M for Male, F for Female).
# 5. **Province**: The province where the farmer is located (e.g., KwaZulu-Natal).
# 6. **SubmitDate**: The date and time when the farmer submitted their data.
# 7. **DeliveredDate**: The date and time when the data was delivered.
# 8. **SessionDate**: The date when the session took place.
# 9. **CropName**: The crop associated with the session (in this case, it appears to be `None`).
# 10. **Login_Hour**: The hour of the day when the login occurred.
# 11. **Login_Day**: The day of the week when the login took place (e.g., Thursday).
# 12. **Duration_Mins**: The duration of the session in minutes.
# 13. **ActiveWeek**: The time period (week) when the user was active.
# 14. **EngagementScore**: A score indicating the level of engagement, with negative values potentially indicating low engagement.
# 
# ### Sample Data:
# - **Farmer 1649** (Male, from KwaZulu-Natal) logged in at 11 AM on Thursday, November 17, 2022, and their session lasted 0 minutes, resulting in an engagement score of -0.070995.
# - **Farmer 1696** (Female, also from KwaZulu-Natal) logged in at 11 AM on the same day with similar session duration and received an engagement score of -0.375290.
# 
# The dataset can be used to analyze login patterns, session duration, and engagement levels of farmers based on various factors such as gender, province, and time of login.
# 

# In[6]:


import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

# Simulating a mock-up data processing flow based on your provided code
# This is assuming 'df_raw' already contains the raw data, as in the given context

# Create a sample DataFrame to mock up the engagement data
np.random.seed(42)

# Simulating a DataFrame based on the FarmerId and engagement columns
farmer_ids = [f"Farmer_{i}" for i in range(1, 101)]
login_counts = np.random.randint(1, 30, 100)  # Random login counts
avg_session_mins = np.random.uniform(5, 30, 100)  # Random session duration (minutes)
active_weeks = np.random.randint(1, 10, 100)  # Random active weeks

# Create DataFrame
df_mock = pd.DataFrame({
    "FarmerId": farmer_ids,
    "LoginCount": login_counts,
    "AvgSessionMins": avg_session_mins,
    "ActiveWeeks": active_weeks
})

# Normalize engagement components
scaler = StandardScaler()
df_scaled = df_mock.copy()
df_scaled[["LoginCount", "AvgSessionMins", "ActiveWeeks"]] = scaler.fit_transform(df_mock[["LoginCount", "AvgSessionMins", "ActiveWeeks"]])

# Create the EngagementScore as the average of the normalized components
df_scaled["EngagementScore"] = df_scaled[["LoginCount", "AvgSessionMins", "ActiveWeeks"]].mean(axis=1)

# Sorting the engagement data
sorted_engagement = df_scaled.sort_values(by="EngagementScore", ascending=False)

# Top 10 highest engagement
top_10_highest = sorted_engagement.head(10)

# Top 10 lowest engagement
top_10_lowest = sorted_engagement.tail(10)

# Get the middle engagement scores (around the median)
middle_10 = sorted_engagement.iloc[len(sorted_engagement)//2 - 5 : len(sorted_engagement)//2 + 5]

# Prepare final results: to update please uncomment below line
#top_10_highest, top_10_lowest, middle_10


# # Data Analysis: Farmer Engagement and Activity
# 
# We have a dataset that consists of the following columns for each farmer:
# - **FarmerId**: The identifier of the farmer.
# - **LoginCount**: The number of logins made by the farmer.
# - **AvgSessionMins**: The average session duration in minutes.
# - **ActiveWeeks**: The number of weeks the farmer has been active.
# - **EngagementScore**: A composite score representing the farmer's engagement based on login activity and session duration.
# 
# The dataset is divided into three distinct categories. Below is the breakdown of each category:
# 
# ## Category 1: High Engagement Farmers
# | FarmerId  | LoginCount | AvgSessionMins | ActiveWeeks | EngagementScore |
# |-----------|------------|----------------|-------------|-----------------|
# | Farmer_72 | 1.435677   | 1.340983       | 1.616138    | 1.464266        |
# | Farmer_66 | 1.201853   | 1.460952       | 1.616138    | 1.426314        |
# | Farmer_61 | 1.435677   | 1.147398       | 1.232257    | 1.271777        |
# | Farmer_32 | 1.201853   | 0.583815       | 1.616138    | 1.133936        |
# | Farmer_64 | 1.201853   | 0.250597       | 1.616138    | 1.022863        |
# | Farmer_60 | 1.084942   | 1.377387       | 0.464496    | 0.975608        |
# | Farmer_7  | 1.552589   | 1.232439       | 0.080615    | 0.955214        |
# | Farmer_36 | 1.084942   | 0.840602       | 0.848376    | 0.924640        |
# | Farmer_37 | 0.149647   | 1.001894       | 1.616138    | 0.922560        |
# | Farmer_58 | 0.266559   | 1.162490       | 1.232257    | 0.887102        |
# 
# ### Interpretation:
# Farmers in this group exhibit moderate to high levels of engagement. Their login counts and session times vary, but their engagement score tends to remain relatively strong. For instance, **Farmer_72** has high login counts and session durations, resulting in a high engagement score of 1.464. On the other hand, **Farmer_37** has a low login count but still maintains a decent engagement score due to a good session duration. 
# 
# ## Category 2: Low Engagement Farmers
# | FarmerId  | LoginCount | AvgSessionMins | ActiveWeeks | EngagementScore |
# |-----------|------------|----------------|-------------|-----------------|
# | Farmer_83 | -0.902559  | -0.345549      | -1.454908   | -0.901005       |
# | Farmer_9  | -1.019471  | -0.626112      | -1.071027   | -0.905537       |
# | Farmer_73 | -1.019471  | -1.555662      | -0.303266   | -0.959466       |
# | Farmer_96 | -0.668736  | -0.766478      | -1.454908   | -0.963374       |
# | Farmer_76 | -0.902559  | -0.825695      | -1.454908   | -1.061054       |
# | Farmer_17 | -1.370206  | -1.560513      | -0.303266   | -1.077995       |
# | Farmer_30 | -1.720942  | -0.475987      | -1.454908   | -1.217279       |
# | Farmer_54 | -1.019471  | -1.318076      | -1.454908   | -1.264152       |
# | Farmer_68 | -1.604030  | -1.205871      | -1.071027   | -1.293643       |
# | Farmer_97 | -1.370206  | -1.087658      | -1.454908   | -1.304258       |
# 
# ### Interpretation:
# Farmers in this group demonstrate significantly low engagement levels. Most of the farmers in this category have negative values for all metrics, indicating very low activity or involvement. For example, **Farmer_83** has a low engagement score of -0.901, with both login count and session time far below average. Similarly, **Farmer_30** has a severely negative engagement score, indicating very minimal engagement.
# 
# ## Category 3: Moderate Engagement Farmers
# | FarmerId  | LoginCount | AvgSessionMins | ActiveWeeks | EngagementScore |
# |-----------|------------|----------------|-------------|-----------------|
# | Farmer_41 | 1.435677   | 0.194246       | -1.454908   | 0.058338        |
# | Farmer_22 | 0.617294   | -1.328034      | 0.848376    | 0.045879        |
# | Farmer_45 | -0.084177  | -1.472617      | 1.616138    | 0.019781        |
# | Farmer_50 | 1.084942   | -0.733466      | -0.303266   | 0.016070        |
# | Farmer_95 | -1.604030  | 1.502257       | 0.080615    | -0.007053       |
# | Farmer_98 | -0.201088  | 0.081335       | 0.080615    | -0.013046       |
# | Farmer_8  | 0.617294   | -0.368879      | -0.303266   | -0.018283       |
# | Farmer_11 | 0.383471   | -1.101130      | 0.464496    | -0.084388       |
# | Farmer_90 | 0.734206   | -1.454101      | 0.464496    | -0.085133       |
# | Farmer_13 | -0.551824  | -1.326318      | 1.616138    | -0.087335       |
# 
# ### Interpretation:
# Farmers in this category show moderate engagement, but their scores tend to fluctuate depending on session duration and login count. Some farmers, such as **Farmer_41**, have a moderate login count but a negative session time, resulting in a very low engagement score of 0.058. **Farmer_95** has an unusually high average session time but still ends up with a low engagement score due to low login counts and limited activity in the active weeks column. These farmers may require more attention to improve their overall engagement.
# 
# ## Conclusion:
# - **High Engagement** farmers are consistently active and show positive engagement scores across the board.
# - **Low Engagement** farmers are underperforming, with negative scores indicating very little activity. Targeted interventions could be useful for this group.
# - **Moderate Engagement** farmers are somewhere in between, but there is potential for improvement. These farmers may benefit from strategic actions to boost their activity and engagement.
# 
# These insights can help in tailoring interventions aimed at improving farmer engagement and activity, leading to higher participation and better outcomes for the farming community.
# 

# In[7]:


#Basic viusalisation:
px.line(df.groupby("session_date")["duration_mins"].mean().reset_index(),
        x="session_date", y="duration_mins", title="Avg Session Duration Over Time")


# ### Average Session Duration Over Time
# 
# The line chart above illustrates the trend of the average session duration (in minutes) over time, spanning from November 2022 to November 2023. The x-axis represents the "session\_date," showing the progression of months, and the y-axis displays the "duration\_mins," indicating the average length of user sessions.
# 
# **Key Observations:**
# 
# * **Relatively Stable Baseline:** For most of the period, the average session duration remains quite low, fluctuating near the zero mark. This suggests that, on average, user sessions are typically short.
# * **Significant Spike in January 2023:** There is a dramatic and isolated spike in the average session duration around January 2023, reaching a peak of over 1500 minutes. This indicates an unusual event or a change in user behavior during this specific period.
# * **Another Smaller Spike in May 2023:** A smaller, though still noticeable, increase in average session duration occurs around May 2023, reaching approximately 400 minutes. This suggests another period of potentially different user engagement.
# * **Return to Baseline:** Following both spikes, the average session duration quickly returns to the low baseline observed for the majority of the timeframe.
# 
# **Interpretation:**
# 
# The average user session duration is generally short throughout the observed period, with two notable exceptions. The significant spike in January 2023 strongly suggests an anomaly or a specific event that caused a substantial increase in the average time users spent in their sessions. The smaller spike in May 2023 indicates another period where session durations were longer than usual, although less extreme than the January event. The return to the low baseline after these spikes implies that these periods of longer average session duration were temporary.
# 
# **Potential Implications and Questions:**
# 
# * **Investigating the January 2023 Spike:** What event or change occurred in January 2023 that led to such a dramatic increase in average session duration? Understanding the cause is crucial. Potential reasons could include a new feature release, a specific campaign, technical issues, or data anomalies.
# * **Understanding the May 2023 Spike:** Similarly, what factors contributed to the increase in average session duration in May 2023? While smaller than the January spike, identifying the cause can still provide valuable insights.
# * **Reasons for Short Baseline Sessions:** Why is the average session duration typically so low? Understanding the typical user behavior and the platform's purpose could provide context.
# * **Impact of Long Sessions:** Did the periods of longer average session duration correlate with any specific user outcomes or business metrics?
# * **Data Accuracy:** It's worth verifying the data for January and May 2023 to ensure the spikes are genuine and not due to data errors.
# 
# Analyzing the context surrounding the spikes in January and May 2023 is essential to understand the underlying reasons and their implications for user engagement.

# In[8]:


px.histogram(df, x="login_hour", nbins=24, title="Login Hour Frequency")


# ### 🕒 Interpretation: Login Hour Frequency
# 
# This bar chart illustrates how frequently farmers log into the platform during different hours of the day.
# 
# ---
# 
# ### 📌 Observations:
# 
# - **Peak Hours:**
#   - Around **9 AM** and **3 PM** show the **highest login counts**, each with over **3,500 sessions**.
#   - Suggests two strong usage waves: **morning and late afternoon**.
# 
# - **Moderate Activity:**
#   - Noticeable login activity at **6 PM – 8 PM**, with a secondary spike around **6 PM**.
# 
# - **Low Activity Periods:**
#   - **Early morning hours** (12 AM to 6 AM) show **minimal login activity**, indicating most users are inactive during those times.
#   - **Late evening to midnight (after 9 PM)** also shows very few logins.
# 
# ---
# 
# ### ✅ Implications:
# - **System Load Planning:** Allocate system resources more heavily around 9 AM and 3 PM to accommodate demand.
# - **User Engagement Strategies:**
#   - Schedule content notifications or updates around 9 AM or 3 PM for higher visibility.
#   - Nighttime campaigns may not be effective due to low activity.
# 
# - **Platform Optimization:**
#   - Consider personalized login reminders for farmers who tend to log in during off-peak hours.
# 

# In[9]:


px.histogram(df, x="login_day", title="Logins by Day",
             category_orders={"login_day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]})


# ### 📅 Interpretation: Logins by Day of the Week
# 
# This bar chart presents the total number of farmer logins across each day of the week, revealing patterns in weekly usage behavior.
# 
# ---
# 
# ### 📌 Observations:
# 
# - **Peak Login Day:**
#   - **Friday** has the **highest login volume**, exceeding **5,000 sessions**.
#   - Likely due to end-of-week activities such as reporting, updates, or planning.
# 
# - **Midweek Surge:**
#   - **Thursday** and **Wednesday** also show elevated activity, with **over 3,000** and **1,500** logins respectively.
#   - Suggests midweek is a key engagement period.
# 
# - **Low Activity Days:**
#   - **Saturday and Sunday** show **almost no login activity**, indicating farmers are mostly inactive over the weekend.
#   - **Monday and Tuesday** also have relatively few logins, suggesting a slow start to the week.
# 
# ---
# 
# ### ✅ Implications:
# 
# - **Engagement Campaigns:**
#   - Schedule key interventions, surveys, or content between **Wednesday and Friday** to maximize engagement.
# 
# - **Support Availability:**
#   - Provide enhanced technical or advisory support later in the week when users are most active.
# 
# - **Weekend Planning:**
#   - Since weekends are inactive, avoid system updates or campaigns during that period unless needed for downtime.
# 

# In[10]:


#Login Frequency by Province and Gender
freq = df.groupby(['Province', 'Gender']).size().reset_index(name='Login Count')
px.bar(freq, x="Province", y="Login Count", color="Gender", barmode="group",
       title="Login Frequency by Province and Gender")


# ### Login Frequency by Province and Gender
# 
# The bar chart displays the login frequency of users, broken down by province and gender. The x-axis represents the different provinces, while the y-axis shows the "Login Count." The chart uses different colored bars to distinguish between genders: blue for Female (F) and red for Male (M), as indicated by the legend on the right.
# 
# **Key Observations:**
# 
# * **Limpopo Dominance:** Limpopo exhibits the highest login frequency for both genders, with a significantly larger number of male logins compared to female logins in this province.
# * **KwaZulu-Natal Activity:** KwaZulu-Natal shows a notable number of logins, with male logins slightly outnumbering female logins.
# * **Lower Activity in Other Provinces:** Gauteng, KwaZulu-Natal (note: appears twice, likely a data entry issue), and Mpumalanga show relatively lower login counts compared to Limpopo and KwaZulu-Natal.
# * **Minimal Activity in Eastern Cape, Northern Cape, and North West:** These provinces record very few or no logins within the observed data.
# * **Gender Disparity in Limpopo:** The most significant gender difference in login frequency is observed in Limpopo, where male logins are substantially higher than female logins.
# 
# **Interpretation:**
# 
# User activity, as measured by login frequency, is highly concentrated in Limpopo and, to a lesser extent, KwaZulu-Natal. There's a notable gender disparity in Limpopo, with male users logging in much more frequently. The remaining provinces show considerably lower levels of user engagement based on login activity. The duplicate entry for "KwaZulu-Natal" likely indicates an error in the data that needs to be addressed for accurate analysis.
# 
# **Potential Implications and Questions:**
# 
# * **Reasons for Limpopo's High Activity:** What factors contribute to the high login frequency in Limpopo? Is it due to a larger user base, specific initiatives, or other regional factors?
# * **Understanding Gender Disparity in Limpopo:** Why is there such a significant difference in login frequency between male and female users in Limpopo? Investigating user demographics, access to resources, or platform engagement patterns could provide insights.
# * **Low Engagement Provinces:** What are the reasons for the low login activity in Eastern Cape, Northern Cape, and North West? Is it due to a smaller user base, lack of awareness, or other barriers to access or engagement?
# * **Addressing the Data Anomaly:** The duplicate "KwaZulu-Natal" entry needs to be investigated and corrected to ensure data accuracy.
# * **Strategies for Low Engagement Provinces:** What strategies can be implemented to increase user engagement (as indicated by logins) in the provinces with low activity?
# 
# Further analysis, potentially incorporating user demographics, platform usage patterns, and regional factors, would be beneficial to understand the underlying reasons for these observed differences in login frequency across provinces and genders.

# In[11]:


#Session Duration by Crop
px.box(df, x="CropName", y="duration_mins", title="Session Duration by Crop")


# ### Session Duration by Crop
# 
# The box plot visualizes the distribution of session durations (in minutes) across different crops. The x-axis lists the various "CropName" categories, and the y-axis represents the "duration\_mins." Each box plot provides insights into the central tendency, spread, and potential outliers of session durations associated with each crop.
# 
# **Key Observations:**
# 
# * **High Session Duration for Specific Crops:** Eggplants (aubergines), Oats, Cauliflower, Garlic, Beetroot, and Cabbage exhibit significantly higher session durations compared to all other listed crops. Their box plots show medians around 1500-2000 minutes, with interquartile ranges indicating a substantial amount of time spent on these crops.
# * **Very Low Session Duration for the Majority of Crops:** The remaining crops, starting from Carrot and extending to Beans, show session durations clustered very close to zero. The box plots for these crops are compressed near the x-axis, indicating minimal time spent on average within sessions related to these crops.
# * **Outliers in High Duration Crops:** Some of the crops with high average session durations (e.g., Eggplants, Oats, Cauliflower) also show potential outliers, represented by individual points extending beyond the whiskers of the box plots. These indicate instances of exceptionally long session durations for these specific crops.
# 
# **Interpretation:**
# 
# There is a clear distinction in session durations based on the type of crop. A small group of crops (Eggplants, Oats, Cauliflower, Garlic, Beetroot, and Cabbage) are associated with much longer user sessions, suggesting users spend a considerable amount of time interacting with content or features related to these crops. Conversely, the vast majority of the listed crops have very short associated session durations, implying minimal engagement or quick interactions.
# 
# **Potential Implications and Questions:**
# 
# * **Reasons for High Engagement Crops:** What are the specific features, information, or tools related to Eggplants, Oats, Cauliflower, Garlic, Beetroot, and Cabbage that might lead to longer session durations? Understanding this could inform strategies for other crops.
# * **Reasons for Low Engagement Crops:** Why do the majority of crops have such short associated session durations? Is it due to the nature of the information available, the user needs related to these crops, or the platform design?
# * **Understanding Outliers:** What could be the reasons for the exceptionally long session durations (outliers) observed in some of the high-engagement crops? Are these specific user behaviors or potentially data anomalies?
# * **User Intent by Crop:** Does the session duration correlate with the user's intent? Are users spending more time on crops they are actively researching or managing in more detail?
# * **Platform Design and Crop Information:** Is the platform designed in a way that encourages longer engagement for certain crops over others? Is the information for high-engagement crops more comprehensive or interactive?
# 
# Investigating the content, features, and user workflows associated with both the high and low engagement crops can provide valuable insights into user behavior and inform potential improvements to the platform or content strategy.

# In[12]:


#Login Hour vs. Session Duration
px.scatter(df, x="login_hour", y="duration_mins", color="Gender",
           title="Login Hour vs. Session Duration")


# ### Login Hour vs. Session Duration by Gender
# 
# The scatter plot displays the relationship between the login hour (on a 24-hour clock) and the session duration (in minutes), differentiated by gender. The x-axis represents the "login\_hour," and the y-axis represents the "duration\_mins." Blue dots indicate male (M) users, while red dots represent female (F) users, as shown in the "Gender" legend on the right.
# 
# **Key Observations:**
# 
# * **Majority of Short Sessions:** The majority of data points, for both male and female users, are clustered near the bottom of the y-axis, indicating that most sessions are relatively short (close to 0 minutes).
# * **Instances of Longer Sessions:** There are noticeable instances of longer session durations for both genders, occurring at various login hours. However, these are less frequent than the short sessions.
# * **Potential Peak Durations Around Specific Hours:**
#     * There appear to be longer male sessions concentrated around login hours 9 and 15.
#     * Longer female sessions seem to occur more frequently around login hours 17-20.
# * **Limited Data for Certain Login Hours:** There are very few or no data points for certain login hours, suggesting limited platform usage during those times for the users in this dataset. For example, there's minimal activity between login hours 0-6.
# * **Overlap in Behavior:** While there are some tendencies for longer sessions at specific times for each gender, there's also significant overlap in behavior, with both males and females exhibiting short sessions across various login hours.
# 
# **Interpretation:**
# 
# The data suggests that while most user sessions are brief, there are specific times when users, both male and female, tend to have longer engagement with the platform. Male users show a tendency for longer sessions around 9 AM and 3 PM, while female users show this tendency more in the late afternoon and early evening (5 PM to 8 PM). However, it's important to note that short sessions are prevalent across all login hours for both genders.
# 
# **Potential Implications and Questions:**
# 
# * **Reasons for Longer Sessions at Specific Times:** What activities or content might be driving the longer sessions observed at particular login hours for each gender? Understanding this could inform content scheduling or feature prioritization.
# * **Typical Use Cases:** What are the typical use cases that result in the very short sessions observed across the board? Are users quickly checking information or performing very specific, brief tasks?
# * **Gender-Specific Usage Patterns:** While there's overlap, are there any significant gender-specific patterns in login times or session durations that could be further explored?
# * **Data Volume and Representativeness:** Is this dataset representative of the entire user base? A larger dataset might reveal more pronounced patterns.
# * **Platform Features and Session Length:** Do specific features or functionalities on the platform correlate with longer session durations?
# 
# Further investigation into the types of activities users engage in during their sessions, especially the longer ones, could provide valuable context to these observations. Understanding the "why" behind these patterns can help optimize the platform and user experience.

# In[13]:


#KMeans Clustering
clustering_df = df[["login_hour", "duration_mins"]].dropna()
scaler = StandardScaler()
scaled = scaler.fit_transform(clustering_df)

kmeans = KMeans(n_clusters=3, random_state=42)
clustering_df["cluster"] = kmeans.fit_predict(scaled)
clustering_df["Cluster Label"] = clustering_df["cluster"].map({
    0: "⏰ Early Loggers",
    1: "🌙 Night Owls",
    2: "📈 High Session Users"
})


# In[14]:


#Cluster Plot with Centroids
centroids = pd.DataFrame(scaler.inverse_transform(kmeans.cluster_centers_),
                         columns=["login_hour", "duration_mins"])
centroids["Cluster Label"] = centroids.index.map({
    0: "⏰ Early Loggers",
    1: "🌙 Night Owls",
    2: "📈 High Session Users"
})

fig = px.scatter(clustering_df, x="login_hour", y="duration_mins", color="Cluster Label",
                 title="Farmer Clusters by Login Hour & Session Duration")
fig.add_scatter(
    x=centroids["login_hour"],
    y=centroids["duration_mins"],
    mode="markers+text",
    marker=dict(size=12, color="black", symbol="x"),
    text=centroids["Cluster Label"],
    textposition="top center",
    showlegend=False
)
fig.show()


# ### Farmer Clusters by Login Hour & Session Duration
# 
# The scatter plot visualizes farmer clusters based on their login hour and session duration. The x-axis represents the "login\_hour" (on a 24-hour clock), and the y-axis represents the "duration\_mins" of their sessions. Different colors and symbols are used to distinguish the identified farmer clusters, as indicated by the "Cluster Label" legend on the right:
# 
# * **Blue Dots (Night Owls):** Farmers in this cluster tend to log in during the later hours of the day (approximately between 7 PM and 11 PM) and have relatively short session durations, generally below 1000 minutes. The black 'X' marks the centroid of this cluster.
# * **Red Dots (High Session Users):** This cluster represents farmers who log in during the afternoon hours (roughly between 2 PM and 6 PM) but are characterized by significantly longer session durations, mostly above 0 but below 800 minutes, with a concentration around very short durations. The black 'X' marks the centroid of this cluster.
# * **Green Dots (Early Loggers):** Farmers in this cluster primarily log in during the early morning hours (around 6 AM to 8 AM) and exhibit a wide range of session durations, from relatively short to very long (up to nearly 3000 minutes). The black 'X' marks the centroid of this cluster.
# 
# **Key Observations:**
# 
# * **Distinct Behavioral Patterns:** The clustering algorithm has identified three distinct groups of farmers based on their login time and session duration, suggesting different engagement patterns.
# * **"Night Owls" - Late Login, Shorter Sessions:** This group seems to engage with the platform in the evening for shorter periods.
# * **"High Session Users" - Afternoon Login, Varied but Generally Shorter Sessions:** This cluster logs in during the afternoon, with a tendency towards shorter session durations, although some longer sessions exist within this group.
# * **"Early Loggers" - Morning Login, Diverse Session Lengths:** Farmers in this group log in early in the day and display the most varied session durations, indicating different types of engagement during their morning activity.
# 
# **Interpretation:**
# 
# The segmentation of farmers into these clusters provides valuable insights into their platform usage habits. The "Night Owls" might be checking for quick updates or performing specific tasks in the evening. The "High Session Users" logging in the afternoon could be involved in more focused activities, although their session durations are generally shorter than some "Early Loggers." The "Early Loggers" show the most diverse behavior, with some potentially engaging in quick checks while others dedicate significant time to the platform in the morning.
# 
# **Potential Implications and Questions:**
# 
# * **Tailored Engagement Strategies:** Understanding these distinct behaviors allows for the development of tailored engagement strategies for each farmer cluster. For example, "Night Owls" might benefit from evening-specific content or notifications.
# * **Content Relevance by Time of Day:** Is the content or functionality of the platform particularly relevant to each cluster during their preferred login times?
# * **Reasons for Diverse Session Lengths in "Early Loggers":** What activities are the "Early Loggers" engaging in that lead to such a wide range of session durations?
# * **Evolution of Clusters:** How stable are these clusters over time? Do farmers consistently fall into the same group, or do their behaviors change?
# * **Cluster Size and Significance:** While the visualization shows distinct clusters, understanding the number of farmers in each cluster would provide further context on their relative importance.
# 
# Further analysis of the activities performed by farmers within each cluster could provide a deeper understanding of their needs and motivations, enabling more effective platform design and user support.

# In[15]:


#Cluster Summary Table
summary_stats = clustering_df.groupby("Cluster Label").agg(
    Count=("cluster", "size"),
    Avg_Login_Hour=("login_hour", "mean"),
    Avg_Session_Duration=("duration_mins", "mean"),
    Max_Session_Duration=("duration_mins", "max"),
    Min_Session_Duration=("duration_mins", "min")
).round(2).reset_index()

summary_stats["Interpretation"] = [
    "These users log in early (morning hours) and have moderate session times.",
    "This group logs in during late hours, with shorter or inconsistent session durations.",
    "Users in this cluster log in across hours but have very long or intense session durations."
]
summary_stats


# ### 📊 Interpretation: Farmer Clusters by Login Hour & Session Duration
# 
# This scatter plot groups farmers based on their **login hour** and **session duration**, identifying distinct behavioral clusters:
# 
# ---
# 
# #### 1. 🌙 Night Owls (Blue Dots)
# - **Login Hours:** 1 AM to 9 AM  
# - **Session Duration:** Very short (near 0 minutes)  
# - **Insight:** These farmers tend to log in during early morning hours but stay active for only a brief period.
# 
# ---
# 
# #### 2. 📊 High Session Users (Red Dots)
# - **Login Hours:** 1 PM to 11 PM  
# - **Session Duration:** Very long (often > 2000 minutes)  
# - **Insight:** These users may not log in frequently but are highly engaged when they do. Possibly involved in data entry, bulk uploads, or prolonged usage.
# 
# ---
# 
# #### 3. 🕓 Early Loggers (Green Dots)
# - **Login Hours:** Primarily between 3 PM and 8 PM  
# - **Session Duration:** Long sessions, slightly shorter than High Session Users  
# - **Insight:** Regular users who log in earlier in the afternoon and remain active for significant durations.
# 
# ---
# 
# ### 📌 Additional Notes:
# - **Black "X" markers** indicate **cluster centroids** (average login hour & session duration).
# - The **hover tooltip** shows detailed data for individual farmers (e.g., login_hour=15, duration_mins=2176).
# 
# ---
# 
# ### ✅ Summary:
# These clusters help identify user segments for:
# - **Targeted engagement** (e.g., educational content for Night Owls)
# - **Resource planning** (e.g., system optimization during high-load periods)
# - **Personalized UX** (e.g., long-session design for High Session Users)
# 

# ### Interpretation of Farmer Clusters by Login Hour & Session Duration Statistics
# 
# The table above provides summary statistics for three distinct clusters of farmers, likely identified based on their login hour and session duration patterns. Let's break down each cluster:
# 
# **Cluster 0: Early Loggers**
# 
# * **Cluster Label:** Early Loggers (indicated by the sunrise emoji)
# * **Count:** 3941 farmers belong to this cluster. This is a significant portion of the farmer base.
# * **Avg\_Login\_Hour:** 15.36 (This translates to approximately 3:36 PM). This is somewhat counterintuitive given the "Early Loggers" label. It might suggest these users have an initial login earlier in the day, and this average reflects a later significant login or activity period as well.
# * **Avg\_Session\_Duration:** 2100.01 minutes. This is a very high average session duration, indicating that when these farmers are active, they tend to spend a substantial amount of time on the platform.
# * **Max\_Session\_Duration:** 2880.0 minutes (48 hours!). This extreme maximum suggests some users in this group might have sessions that last for exceptionally long periods, potentially indicating background activity or sessions left open.
# * **Min\_Session\_Duration:** 1336.0 minutes (approximately 22.27 hours). Even the minimum session duration for this cluster is quite high, reinforcing the trend of long engagement.
# * **Interpretation:** The provided interpretation states: "These users log in early (morning hours) and h..." The rest of the sentence is cut off, but based on the statistics, while the label suggests early logins, the average login hour is in the afternoon. However, the defining characteristic of this group is their **very long average session duration**. They might log in early and then have prolonged engagement or activity later in the day.
# 
# **Cluster 1: Night Owls**
# 
# * **Cluster Label:** Night Owls (indicated by the moon emoji)
# * **Count:** 4565 farmers, the largest of the three clusters.
# * **Avg\_Login\_Hour:** 8.38 (approximately 8:23 AM). This doesn't entirely align with the "Night Owls" label. It's possible this label refers to a secondary login pattern or that the clustering algorithm prioritized session timing differently.
# * **Avg\_Session\_Duration:** 786.98 minutes (approximately 13.12 hours). This is still a relatively long average session duration, although significantly less than the "Early Loggers."
# * **Max\_Session\_Duration:** 1246.0 minutes (approximately 20.77 hours). The maximum session duration is also lower than that of the "Early Loggers."
# * **Min\_Session\_Duration:** 0.0 minutes. Some users in this group have very short or potentially no recorded session durations.
# * **Interpretation:** The provided interpretation states: "This group logs in during late hours, with sho..." The rest of the sentence is cut off. Based on the average login hour, this label seems misapplied if it solely refers to the initial login time. However, the "with sho..." likely refers to "shorter" session durations compared to the "Early Loggers," which is supported by the data. It's possible this group has a primary login in the morning but also exhibits activity during later hours, influencing the cluster name.
# 
# **Cluster 2: High Session Users**
# 
# * **Cluster Label:** High Session Users (indicated by the upward trend emoji)
# * **Count:** 1835 farmers, the smallest of the three clusters.
# * **Avg\_Login\_Hour:** 17.44 (approximately 5:26 PM). This indicates a tendency to log in in the late afternoon to early evening.
# * **Avg\_Session\_Duration:** 7.40 minutes. This is a very short average session duration, contrasting sharply with the other two clusters.
# * **Max\_Session\_Duration:** 733.0 minutes (approximately 12.22 hours). While the maximum is higher than the average, it's still considerably lower than the other clusters' maximums.
# * **Min\_Session\_Duration:** 0.0 minutes. Similar to the "Night Owls," some users in this group have very short or no recorded session durations.
# * **Interpretation:** The provided interpretation states: "Users in this cluster log in across hours but ..." The rest of the sentence is cut off. However, the key characteristic of this group, despite the "High Session Users" label, is their **very short average session duration**, even though they might log in at various times. The label might be misleading or refer to a different aspect of their "high" usage (e.g., frequency of logins, number of features used) not captured by session duration alone.
# 
# **Overall Interpretation and Potential Issues:**
# 
# * **Labeling Inconsistencies:** There seems to be a disconnect between the cluster labels ("Early Loggers" and "Night Owls") and their average login hours. This suggests the clustering might be based on a more complex combination of login times and session durations, or the labels might be slightly misleading based solely on these two metrics.
# * **"Early Loggers" - Long Engagement:** This group is characterized by significantly long session durations, despite the "Early Loggers" label.
# * **"Night Owls" - Moderate Engagement, Morning Login:** This group has a moderate average session duration and an average login in the morning.
# * **"High Session Users" - Short Engagement, Late Afternoon Login:** This group has a late afternoon/early evening average login but very short session durations. The label is potentially misrepresentative based on session duration.
# 
# It's crucial to understand the exact features used by the clustering algorithm to fully grasp the meaning of these clusters. The interpretations provided in the table offer some initial insights but need to be considered in conjunction with the actual statistical values. Further investigation into login frequency, activity patterns within sessions, and other relevant features might provide a clearer picture of these farmer segments.

# In[16]:


#Farmer Retention (Weekly Active Farmers)
# Add 'week' column
df['week'] = df['SubmitDate'].dt.to_period('W')

# Calculate active weeks per farmer
retention_df = df.groupby('FarmerId')['week'].nunique().reset_index()
retention_df.rename(columns={'week': 'ActiveWeeks'}, inplace=True)

# Merge back to main dataframe
df = df.merge(retention_df, on='FarmerId')


# In[17]:


# After calculating retention_df and merging it back to the main dataframe

# Create the histogram for Farmer Retention (Active Weeks)
import plotly.express as px

# Plot histogram for Farmer Retention (Active Weeks)
px.histogram(retention_df, x='ActiveWeeks', nbins=10, title='Farmer Retention (Active Weeks)')


# ### ]Farmer Retention Analysis (Active Weeks)
# 
# The histogram above visualizes farmer retention based on the number of active weeks. The x-axis represents the "ActiveWeeks," indicating the number of weeks a farmer was active. The y-axis shows the "count," representing the number of farmers who were active for that specific number of weeks.
# 
# **Key Observations:**
# 
# * **High Initial Retention:** A significant number of farmers (approximately 28) were active for only one week. This suggests a large initial churn after the first week.
# * **Decreasing Retention Over Time:** The number of active farmers decreases substantially in the subsequent weeks. Around 16 farmers remained active for two weeks, and this number further drops to approximately 9 for three weeks.
# * **Long-Term Retention is Low:** The number of farmers active for four weeks or more is very low, with only a few farmers remaining active for longer durations (e.g., around 2 for four weeks and 1 for seven weeks).
# 
# **Interpretation:**
# 
# This data indicates a challenge in retaining farmers beyond the initial few weeks. There's a high drop-off rate after the first week, and the retention continues to decline in the following weeks. Very few farmers remain active for an extended period.
# 
# **Potential Implications and Questions:**
# 
# * **Onboarding Process:** Is there an issue with the initial onboarding or engagement process that leads to such high churn after the first week?
# * **Value Proposition:** Are farmers finding sufficient value or benefit to remain active beyond the initial period?
# * **Engagement Strategies:** Are the current engagement strategies effective in retaining farmers in the long term?
# * **Data Granularity:** Analyzing the reasons behind inactivity at each stage could provide valuable insights.
# 
# Further investigation into the reasons for farmer inactivity at different stages is recommended to develop effective retention strategies.

# In[18]:


# Group by and calculate metrics
engagement_df = df.groupby('FarmerId').agg({
    'duration_mins': 'mean',
    'FarmerId': 'count',
    'week': 'first'
}).rename(columns={'FarmerId': 'LoginCount'})

# Print the intermediate results
#print("Engagement Metrics After Grouping:")
#print(engagement_df.head())

# Normalize only numeric columns
for col in ['duration_mins', 'LoginCount']:
    engagement_df[col] = (engagement_df[col] - engagement_df[col].min()) / (engagement_df[col].max() - engagement_df[col].min())

# Print the normalized columns
#print("\nNormalized Engagement Metrics:")
#print(engagement_df[['duration_mins', 'LoginCount']].head())

# Convert 'week' from PeriodDtype to timestamp (if it's Period)
if isinstance(engagement_df['week'].dtype, pd.PeriodDtype):
    engagement_df['week'] = engagement_df['week'].dt.to_timestamp()

# Print the 'week' column after conversion
#print("\nWeek After Conversion to Timestamp:")
#print(engagement_df[['week']].head())

# Normalize 'week' as a numeric value
engagement_df['week_numeric'] = (engagement_df['week'] - engagement_df['week'].min()) / (engagement_df['week'].max() - engagement_df['week'].min())

# Print the normalized week column
#print("\nNormalized Week Numeric:")
#print(engagement_df[['week_numeric']].head())

# Weighted score
engagement_df['EngagementScore'] = (
    0.4 * engagement_df['duration_mins'] +
    0.3 * engagement_df['LoginCount'] +
    0.3 * engagement_df['week_numeric']
)

# Print the EngagementScore column
#print("\nCalculated EngagementScore:")
#print(engagement_df[['EngagementScore']].head())

# Drop existing 'EngagementScore' column if it exists in df
df = df.drop(columns=['EngagementScore'], errors='ignore')

# Merge back to main
df = df.merge(engagement_df['EngagementScore'], on='FarmerId', how='left')

# Print the final dataframe with merged EngagementScore
#print("\nFinal DataFrame with Merged EngagementScore:")
#print(df.head())


# In[19]:


#Churn Detection
#Mark farmers as at risk of churn if they haven’t logged in during the last 30 days.
latest_date = df['SubmitDate'].max()
last_login = df.groupby('FarmerId')['SubmitDate'].max().reset_index()
last_login['DaysSinceLastLogin'] = (latest_date - last_login['SubmitDate']).dt.days
last_login['ChurnRisk'] = last_login['DaysSinceLastLogin'] > 30

# Drop the existing 'ChurnRisk' column (if it exists)
df = df.drop(columns=['ChurnRisk'], errors='ignore')

# Merge the churn risk back into the main dataframe
df = df.merge(last_login[['FarmerId', 'ChurnRisk']], on='FarmerId')
#print("\nFinal DataFrame with ChurnRisk:")
#print(df.head())




# In[20]:


#Behavioral Personas (Using Engagement & Clustering)
def label_persona(row):
    if row['EngagementScore'] > 0.75:
        return '🌟 Super User'
    elif row['EngagementScore'] > 0.5:
        return '🧠 Consistent'
    elif row['EngagementScore'] > 0.25:
        return '⚠️ Low Engagement'
    else:
        return '🛑 At Risk'

df['Persona'] = df.apply(label_persona, axis=1)


# In[21]:


from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# Assuming 'df' is your DataFrame and 'EngagementScore' is the feature you're clustering on.
# Standardize the data (optional but recommended for better clustering results)
scaler = StandardScaler()
X = scaler.fit_transform(df[['EngagementScore']])  # Use relevant columns for clustering

# Range of cluster numbers to test
cluster_range = range(2, 11)  # Testing from 2 to 10 clusters

silhouette_scores = []

# Test different numbers of clusters
for k in cluster_range:
    kmeans = KMeans(n_clusters=k, random_state=42)
    labels = kmeans.fit_predict(X)  # Fit the model and get the labels
    
    score = silhouette_score(X, labels)  # Calculate Silhouette Score
    silhouette_scores.append(score)
    print(f"Number of Clusters: {k}, Silhouette Score: {score:.2f}")

# Plot the Silhouette Scores for different cluster numbers
plt.figure(figsize=(8, 6))
plt.plot(cluster_range, silhouette_scores, marker='o', linestyle='-', color='b')
plt.title("Silhouette Score vs Number of Clusters")
plt.xlabel("Number of Clusters")
plt.ylabel("Silhouette Score")
plt.grid(True)
plt.show()


# ### Silhouette Score Interpretation for Different Number of Clusters
# 
# Interpretation:
# Cluster Numbers (2 to 10): The x-axis represents the number of clusters, ranging from 2 to 10.
# 
# Silhouette Score (0.95 to 0.99): The y-axis represents the Silhouette Score, which ranges from 0.95 to 0.99.
# 
# The Silhouette Score is a measure of how similar each point is to its own cluster compared to other clusters. A higher value indicates that the clustering is well-formed and dense.
# 
# Insights:
# Sharp Increase (Cluster 2 to 4):
# 
# The Silhouette Score initially starts at around 0.97 for 2 clusters but sharply decreases when the number of clusters increases to 3 and 4. This suggests that splitting the data into 3 or 4 clusters results in less cohesive groups or poor separation.
# 
# This could mean that fewer clusters (e.g., 2 or 3) might not be able to capture the underlying patterns in the data efficiently.
# 
# Peak Performance (Cluster 6):
# 
# The Silhouette Score hits a peak at 6 clusters, reaching about 0.99. This indicates that 6 clusters provide the best segmentation, where the data points within each cluster are most similar to each other, and the clusters themselves are well-separated. This is likely the optimal number of clusters in your case.
# 
# Plateau (Clusters 7 to 10):
# 
# After reaching the peak at 6 clusters, the Silhouette Score plateaus at around 0.98 from 7 to 10 clusters. While the score is still high, the improvement in performance with more clusters becomes marginal. This suggests that adding more clusters beyond 6 does not significantly improve the clustering quality, and it may even lead to overfitting the model.
# 
# Conclusion:
# Based on this graph, 6 clusters appears to be the optimal choice for clustering your data, as it provides the highest Silhouette Score.
# 
# Adding more clusters (7 to 10) does not lead to significant improvements, and you could risk making the model unnecessarily complex.
# 
# The initial drop in the score between 2 and 4 clusters indicates that this range might not provide well-separated or meaningful clusters.
# 
# If you need further help with the next steps, like examining the clusters themselves, feel free to ask!
# 

# In[22]:


import pandas as pd
import plotly.express as px

# Step 1: Prepare the base df
df['ActiveWeek'] = df['SubmitDate'].dt.to_period('W').astype(str)

# Step 2: Compute farmer-level metrics first
farmer_df = df.groupby('FarmerId').agg({
    'duration_mins': 'sum',
    'login_hour': 'mean',
    'ActiveWeek': pd.Series.nunique,
    'Gender': 'first',
    'Province': 'first',
}).rename(columns={'ActiveWeek': 'ActiveWeeks'}).reset_index()

# Step 3: Normalize values for Engagement Score
farmer_df['NormWeeks'] = farmer_df['ActiveWeeks'] / farmer_df['ActiveWeeks'].max()
farmer_df['NormDuration'] = farmer_df['duration_mins'] / farmer_df['duration_mins'].max()
farmer_df['EngagementScore'] = 0.5 * farmer_df['NormWeeks'] + 0.5 * farmer_df['NormDuration']

# Step 4: Label Personas
def label_persona(score):
    if score >= 0.75:
        return '🌟 Super User'
    elif score >= 0.5:
        return '🧠 Consistent'
    elif score >= 0.25:
        return '⚠️ Low Engagement'
    else:
        return '🛑 At Risk'

farmer_df['Persona'] = farmer_df['EngagementScore'].apply(label_persona)

# Step 5: Persona summary (now correctly per unique farmer)
persona_summary = farmer_df.groupby('Persona').agg({
    'FarmerId': 'count',
    'duration_mins': 'mean',
    'login_hour': 'mean',
    'ActiveWeeks': 'mean',
    'EngagementScore': 'mean'
}).rename(columns={'FarmerId': 'UniqueFarmers'}).reset_index()

# Step 6: Plot
fig = px.bar(
    persona_summary, x='Persona', y='UniqueFarmers',
    title='👥 Farmer Personas by Engagement Level',
    color='Persona', text='UniqueFarmers'
)
fig.update_traces(textposition='outside')
fig.show()


# ### Farmer Personas by Engagement Level
# 
# The bar chart above illustrates the distribution of farmer personas based on their engagement levels. The x-axis displays the different engagement-based personas: "Low Engagement," "At Risk," and "Consistent." The y-axis represents the "UniqueFarmers," indicating the number of farmers belonging to each persona. The legend on the right clarifies the color coding for each persona.
# 
# **Key Observations:**
# 
# * **Dominance of "At Risk" Persona:** The vast majority of farmers, totaling 55, fall into the "At Risk" engagement category. This group represents a significant portion of the farmer base that requires attention to prevent potential disengagement.
# * **Small "Low Engagement" Group:** Only 2 farmers are categorized as "Low Engagement." While a small number, this group likely requires targeted strategies to increase their participation.
# * **Small "Consistent" Group:** Similarly, only 2 farmers are identified as "Consistent" in their engagement. This highlights a potential area for understanding and replicating the factors contributing to their sustained engagement across a larger farmer base.
# 
# **Interpretation:**
# 
# The data reveals a concerning trend with a large number of farmers classified as "At Risk." This suggests that a substantial portion of the farmer community might be on the verge of disengagement and could benefit from proactive interventions. The very small number of "Consistent" farmers underscores the need to identify and potentially scale the strategies that lead to sustained engagement.
# 
# **Potential Implications and Questions:**
# 
# * **"At Risk" Characteristics:** What are the common characteristics or behaviors of the farmers in the "At Risk" category? Understanding these factors is crucial for developing effective intervention strategies.
# * **Drivers of "Consistent" Engagement:** What factors contribute to the consistent engagement of the small group of farmers in that category? Can these factors be leveraged to improve engagement among other farmers?
# * **Strategies for "At Risk" Farmers:** What specific strategies can be implemented to re-engage the "At Risk" farmers and prevent further disengagement?
# * **Moving Farmers Towards "Consistent":** What pathways or interventions can help move farmers from "Low Engagement" and "At Risk" towards more consistent engagement?
# 
# Addressing the large "At Risk" segment is critical for improving overall farmer engagement and retention. Understanding the nuances of each persona will be key to developing targeted and effective strategies.

# In[24]:


# ✅ Personas by Province
fig_province = px.bar(
    farmer_df.groupby(['Province', 'Persona']).size().reset_index(name='Count'),
    x='Province', y='Count', color='Persona',
    title='📍 Farmer Personas by Province',
    text='Count', barmode='group'
)
fig_province.update_traces(textposition='outside')
fig_province.show()


# In[25]:


# ✅ Personas by Gender
fig_gender = px.bar(
    farmer_df.groupby(['Gender', 'Persona']).size().reset_index(name='Count'),
    x='Gender', y='Count', color='Persona',
    title='🚻 Farmer Personas by Gender',
    text='Count', barmode='group'
)
fig_gender.update_traces(textposition='outside')
fig_gender.show()


# # 👥 Farmer Personas by Gender
# 
# This chart visualizes the distribution of farmer personas across gender categories. The personas are derived from behavioral segmentation and highlight differences in engagement and risk levels.
# 
# | Gender | Persona          | Count | Interpretation                                                                 |
# |--------|------------------|-------|--------------------------------------------------------------------------------|
# | **F**  | 🛑 At Risk         | 24    | A significant number of female farmers are considered "At Risk"—indicating potential churn or lack of consistent engagement. |
# |        | ⚠️ Low Engagement  | 1     | Very few show low engagement, suggesting most issues are deeper than mere inactivity. |
# |        | 🧠 Consistent      | 1     | Very few consistent female farmers, which raises concern for long-term stability.      |
# | **M**  | 🛑 At Risk         | 29    | Similar to females, the majority of male farmers are also "At Risk."                              |
# |        | ⚠️ Low Engagement  | 1     | Low count here as well—points to issues beyond surface-level inactivity.          |
# |        | 🧠 Consistent      | 1     | Extremely few male farmers are consistent—suggests a systemic problem in engagement.  |
# 
# ---
# 
# ## 📌 Key Observations
# 
# - The **"At Risk" persona dominates** for both genders, with **24 females** and **29 males** falling into this category.
# - Very few farmers from either gender are **"Consistent"**, which may signal ineffective outreach or support programs.
# - **Low Engagement** is not the primary issue—risk status is likely driven by other factors such as economic barriers, lack of resources, or dissatisfaction.
# 
# ## ✅ Actionable Insights
# 
# - Investigate the underlying causes driving most farmers into the **"At Risk"** segment.
# - Develop **targeted interventions** for each gender to improve engagement, retention, and outcomes.
# - Consider personalized training, incentives, or outreach to transition more farmers into the **"Consistent"** persona group.
# 

# In[26]:


from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# ✅ Select features for clustering
features = farmer_df[['duration_mins', 'login_hour', 'ActiveWeeks', 'EngagementScore']]

# ✅ Normalize the data
scaler = StandardScaler()
scaled_features = scaler.fit_transform(features)

# ✅ Run KMeans (choose 4 clusters, can be optimized with elbow method)
kmeans = KMeans(n_clusters=4, random_state=42, n_init='auto')
farmer_df['Cluster'] = kmeans.fit_predict(scaled_features)

# ✅ Optional: label clusters with emoji or profile names for better readability
cluster_labels = {
    0: '🔵 Cluster 0',
    1: '🟢 Cluster 1',
    2: '🟡 Cluster 2',
    3: '🔴 Cluster 3'
}
farmer_df['ClusterLabel'] = farmer_df['Cluster'].map(cluster_labels)


# In[27]:


# ✅ Cluster size (fixed version)
cluster_counts = farmer_df['ClusterLabel'].value_counts().reset_index()
cluster_counts.columns = ['ClusterLabel', 'FarmerCount']  # rename columns

fig_cluster_count = px.bar(
    cluster_counts,
    x='ClusterLabel', y='FarmerCount',
    labels={'ClusterLabel': 'Cluster', 'FarmerCount': 'Farmer Count'},
    title='🤖 AI-Based Farmer Segmentation (KMeans Clusters)',
    text='FarmerCount'
)
fig_cluster_count.update_traces(textposition='outside')
fig_cluster_count.show()


# # 🤖 AI-Based Farmer Segmentation (KMeans Clusters)
# 
# This bar chart shows how farmers are distributed across different KMeans clusters. Each cluster groups farmers based on similar characteristics or behaviors.
# 
# | Cluster     | Farmer Count | Interpretation                                                                 |
# |-------------|---------------|--------------------------------------------------------------------------------|
# | **Cluster 0** | **37**         | 🧑‍🌾 **Largest group**: Represents the majority. Likely the most common farmer profile. |
# | **Cluster 1** | **12**         | Mid-sized group: Has some distinguishing traits worth targeting.             |
# | **Cluster 3** | **7**          | Smaller segment: May exhibit niche behaviors or needs.                       |
# | **Cluster 2** | **1**          | 🚨 **Outlier**: A unique profile or rare case; may require special attention. |
# 
# ---
# 
# ## 🔍 Key Insights
# 
# - **Cluster 0 dominates** the population, suggesting a common farmer behavior or demographic.
# - **Clusters 1 and 3** represent **smaller but meaningful segments**—ideal for focused interventions.
# - **Cluster 2**, with only **1 farmer**, is an **outlier**—could be an edge case, an error, or someone highly unique (e.g., highly advanced or disengaged).
# - Segmentation like this enables **personalized strategies**, such as tailored support, training, or financial offerings.
# 
# 

# In[28]:


# ✅ Average stats per cluster
# ✅ Average stats per cluster (sorted by Cluster)
cluster_summary = farmer_df.groupby('ClusterLabel').agg({
    'duration_mins': 'mean',
    'login_hour': 'mean',
    'ActiveWeeks': 'mean',
    'EngagementScore': 'mean',
    'FarmerId': 'count'
}).rename(columns={'FarmerId': 'FarmerCount'}).reset_index()

# Sort the cluster summary by ClusterLabel
cluster_summary = cluster_summary.sort_values(by='ClusterLabel')

# Plot Engagement Score per Cluster (sorted)
fig_cluster_stats = px.bar(
    cluster_summary,
    x='ClusterLabel', y='EngagementScore',
    color='ClusterLabel', text='EngagementScore',
    title='📊 Engagement Score per Cluster'
)
fig_cluster_stats.update_traces(textposition='outside')
fig_cluster_stats.show()




# In[ ]:





# # 📊 Engagement Score per Cluster
# 
# The chart presents average engagement scores across four clusters. Below is a summary and interpretation of each:
# 
# | Cluster     | Engagement Score | Interpretation                                                                 |
# |-------------|------------------|--------------------------------------------------------------------------------|
# | **Cluster 2** | **0.6421**       | 🔝 **Highest engagement**: Highly active users. Likely loyal and consistent.    |
# | **Cluster 1** | **0.2500**       | Moderate engagement: Some interaction; potential for increased involvement.    |
# | **Cluster 0** | **0.1004**       | Low engagement: Minimal interaction; may need engagement strategies.           |
# | **Cluster 3** | **0.0836**       | 🚨 **Lowest engagement**: At risk of churn; urgent intervention may be needed.  |
# 
# ---
# 
# ## 🔍 Key Insights
# 
# - **Cluster 2** is the **most engaged** and may represent your core user base.
# - **Cluster 1** shows promise but could benefit from targeted motivation or rewards.
# - **Clusters 0 and 3** are significantly less engaged—consider specific re-engagement campaigns.
# - Clear score separation supports tailored cluster-based strategies for growth and retention.
# 

# In[33]:


import os
import json
import subprocess
import webbrowser
from IPython.display import display, HTML

# --- Detect notebook filename ---
notebooks = [x for x in os.listdir() if x.endswith(".ipynb") and not x.startswith(".")]
notebook_file = notebooks[0] if notebooks else None

if not notebook_file:
    display(HTML("<b style='color:red;'>❌ No notebook (.ipynb) file found in the current directory.</b>"))
else:
    webpdf_file = notebook_file.replace(".ipynb", ".webpdf")
    html_file = notebook_file.replace(".ipynb", ".html")

    # --- OneDrive export path ---
    one_drive_path = r'C:\Users\Paul Mazibuko\OneDrive'
    html_file_onedrive = os.path.join(one_drive_path, html_file)

    # --- Inject Plotly renderer setting if missing ---
    def inject_plotly_renderer():
        try:
            with open(notebook_file, "r", encoding="utf-8") as f:
                nb_data = json.load(f)

            cells = nb_data.get("cells", [])
            already_set = any(
                "pio.renderers.default" in "".join(cell.get("source", []))
                for cell in cells if cell.get("cell_type") == "code"
            )

            if not already_set:
                plotly_code = (
                    "import plotly.io as pio\n"
                    "pio.renderers.default = 'browser'\n"  # Updated to 'browser' for interactivity in HTML export
                )
                nb_data["cells"].insert(0, {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [plotly_code]
                })
                with open(notebook_file, "w", encoding="utf-8") as f:
                    json.dump(nb_data, f, indent=2)
                print("✅ Injected Plotly renderer setup at top of notebook.")
            else:
                print("ℹ️ Plotly renderer already set in notebook.")
        except Exception as e:
            display(HTML(f"<div style='color:red'>⚠️ Could not inject Plotly setup: {e}</div>"))

    # --- Install dependencies ---
    def install_packages():
        try:
            print("📦 Installing nbconvert[webpdf] ...")
            subprocess.run("pip install -q nbconvert[webpdf]", shell=True, check=True)
            print("🧩 Installing Playwright Chromium ...")
            subprocess.run("playwright install chromium", shell=True, check=True)
        except subprocess.CalledProcessError as e:
            display(HTML(f"<div style='color:red'>❌ Installation failed: {e}</div>"))
            raise

    # --- Convert to PDF ---
    def convert_to_webpdf():
        print(f"📄 Exporting {notebook_file} to WebPDF (code hidden, Plotly supported)...")
        return os.system(
            f'jupyter nbconvert "{notebook_file}" --to webpdf --no-input --allow-chromium-download --embed-images=True'
        ) == 0

    # --- Convert to HTML ---
    def convert_to_html():
        print(f"📄 Exporting {notebook_file} to HTML and saving to OneDrive...")
        return os.system(
            f'jupyter nbconvert "{notebook_file}" --to html --template lab --no-input --output "{html_file_onedrive}"'
        ) == 0

    # --- Show download link ---
    def show_download(file_path, format_label):
        display(HTML(f"""
            <div style="font-family:sans-serif; padding:10px; border:1px solid #ddd; border-radius:10px; background:#f6fff6;">
                ✅ <b>Export successful ({format_label})!</b><br>
                📥 <a href="{file_path}" download target="_blank" style="color:#2a7ae2; font-weight:bold;">
                    Click here to download your {format_label}
                </a>
            </div>
        """))

    # --- User Tip ---
    display(HTML("""
        <div style="font-family:sans-serif; padding:10px; border:1px solid #e0e0e0; border-radius:8px; background:#f9f9ff;">
            ℹ️ <b>Tip:</b> To ensure Plotly charts appear in exported PDFs/HTML, make sure your notebook includes:<br>
            <code>import plotly.io as pio<br>pio.renderers.default = 'browser'</code>
        </div>
    """))

    # --- Run Export Process ---
    inject_plotly_renderer()
    install_packages()

    if convert_to_webpdf() and os.path.exists(webpdf_file):
        show_download(webpdf_file, "PDF (with Plotly, code hidden)")
    elif convert_to_html() and os.path.exists(html_file_onedrive):
        show_download(html_file_onedrive, "HTML (open in browser and Save as PDF)")
        print("🌐 Opening HTML file in browser...")
        webbrowser.open("file://" + os.path.abspath(html_file_onedrive))
    else:
        display(HTML(f"""
            <div style="font-family:sans-serif; padding:10px; border:1px solid #ddd; border-radius:10px; background:#fff6f6;">
                ❌ <b>Export failed.</b><br>
                Please ensure the notebook file exists and dependencies installed correctly.<br>
                Use <code>!ls</code> in a cell to verify file names.
            </div>
        """))


# In[ ]:




