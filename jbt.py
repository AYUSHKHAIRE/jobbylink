import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import seaborn as sns

# giving the headings to our app
st.title("LinkedIn Job Postings")
df = pd.read_csv("postings.csv")
# reading the dataset . I will convert all to lowercase to avoid conflict between Python and python
maindf = df.applymap(lambda x: x.lower() if isinstance(x, str) else x)


# side bar
st.sidebar.subheader("Filters")
st.sidebar.write("click on options and start typing to search ...")
# listing all the unique values from the remarkable columns
job_titles = st.sidebar.multiselect(
    "Select job title",
    options=maindf['job_title'].unique(),
    default=maindf['job_title'].unique()[:30],
    key="job_titles_multiselect"
)

company = st.sidebar.multiselect(
    "Select company",
    options=maindf['company'].unique(),
    default=maindf['company'].unique()[:30],
    key="company_multiselect",
)

job_location = st.sidebar.multiselect(
    "Select job location",
    options=maindf['job_location'].unique(),
    default=maindf['job_location'].unique()[:30],
    key="job_location_multiselect"
)

search_city = st.sidebar.multiselect(
    "Select search city",
    options=maindf['search_city'].unique(),
    default=maindf['search_city'].unique()[:30],
    key="search_city_multiselect"
)

search_country = st.sidebar.multiselect(
    "Select search country",
    options=maindf['search_country'].unique(),
    default=maindf['search_country'].unique()[:30],
    key="search_country_multiselect"
)

job_level = st.sidebar.multiselect(
    "Select job level",
    options=maindf['job_level'].unique(),
    default=maindf['job_level'].unique()[:30],
    key="job_level_multiselect"
)

job_type = st.sidebar.multiselect(
    "Select job type",
    options=maindf['job_type'].unique(),
    default=maindf['job_type'].unique()[:30],
    key="job_types_multiselect"
)
first_seen = st.sidebar.multiselect(
    "Select first_seen",
    options=maindf['first_seen'].unique(),
    default=maindf['first_seen'].unique()[:30],
    key="first_seen_multiselect"
)


# skills treatment
def skillsetmaker(dataframe):
    # empty list
    list_skill = []
    for skill_set in dataframe['job_skills']:
        # if list is not none
        if pd.notna(skill_set):
            # split different skills and extend to list
            skills = skill_set.split(",")
            list_skill.extend(skills)
        else:
            list_skill.extend([])
    # make a set of it ; as we need uniques
    unique_skills_set = set(list_skill)
    return unique_skills_set


skill_set = []
all_unique_skills = skillsetmaker(maindf)
# now listify it again
all_unique_skills_list = list(all_unique_skills)
skill_set = skillsetmaker(maindf)
skill_set = st.sidebar.multiselect(
    "Select skill set",
    options=all_unique_skills_list,
    default=all_unique_skills_list[:1000],
    key="skill_set_multiselect"
)

# handle qurries
title_mask = maindf['job_title'].isin(job_titles)
company_mask = maindf['company'].isin(company)
location_mask = maindf['job_location'].isin(job_location)
city_mask = maindf['search_city'].isin(search_city)
country_mask = maindf['search_country'].isin(search_country)
type_mask = maindf['job_type'].isin(job_type)
level_mask = maindf['job_level'].isin(job_level)
first_seen = maindf['first_seen'].isin(first_seen)
skills_mask = maindf['job_skills'].apply(
    # this will see if any selected skill present
    lambda skills_list: any(skill in skills_list for skill in skill_set) if pd.notna(
        skills_list) else False
)

df_selection = maindf[
    title_mask & company_mask & location_mask & city_mask & country_mask & type_mask & level_mask & skills_mask & first_seen
]


def Home():
    # top analytics
    with st.expander("tabular"):
        showData = st.multiselect(
            'filter : ', df_selection.columns, default=[])
        st.write(df_selection[showData])
    total_roles = maindf['job_title'].nunique()
    total_positions = len(maindf['job_title'])
    total_companies = maindf['company'].nunique()
    total_locations = maindf['job_location'].nunique()
    topana1, topana2, topana3, topana4 = st.columns(4, gap='large')
    with topana1:
        st.metric(label="job roles", value=f"{total_roles}")
    with topana2:
        st.metric(label="Positions", value=f"{total_positions}")
    with topana3:
        st.metric(label="Companies", value=f"{total_companies}")
    with topana4:
        st.metric(label="Locations", value=f"{total_locations}")

    st.dataframe(df_selection)


def job_roles_distribution():
    # Assuming df_selection is your DataFrame containing job data
    job_roles_counts = df_selection['job_title'].value_counts()
    job_roles = job_roles_counts.index
    counts = job_roles_counts.values
    n_colors = len(job_roles)
    colors = sns.color_palette("Blues", n_colors=n_colors)
    fig, ax = plt.subplots(figsize=(12, len(job_roles) / 2))
    bars = ax.barh(job_roles, counts, color=colors,
                   edgecolor='black', linewidth=1.2)

    for bar, count in zip(bars, counts):
        xval = bar.get_width()
        ax.text(xval + 0.1, bar.get_y() +
                bar.get_height() / 2, count, va='center')
    ax.set_xlabel('Count')
    ax.set_title('Job Roles Distribution')
    ax.set_ylabel('Job Roles')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    st.pyplot(fig)


def companies_offered_position_distribution():
    companies_counts = df_selection['company'].value_counts()
    fig, ax = plt.subplots(figsize=(12, 6))
    n_colors = len(companies_counts)
    colors = sns.color_palette("Greens", n_colors=n_colors)
    ax.bar(companies_counts.index, companies_counts.values,
           color=colors, edgecolor='black', linewidth=1.2)
    ax.set_xlabel('Company Name')
    ax.set_ylabel('Number of Positions Offered')
    ax.set_title('Distribution of Positions Offered by Companies')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig)


def available_locations():
    locations = df_selection['job_location'].value_counts()
    colors = sns.color_palette("pink", len(locations))
    explode = [0.1] + [0] * (len(locations) - 1)
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(locations, labels=locations.index, autopct='%1.1f%%', startangle=90,
           colors=colors, wedgeprops=dict(width=0.3, edgecolor='w'),
           shadow=True, explode=explode)
    ax.set_title('Distribution of Job Locations')
    st.pyplot(fig)


def skillplotter():
    list_skill = []
    for skill_set in df_selection['job_skills']:
        if pd.notna(skill_set) and not isinstance(skill_set, bool):
            skills = skill_set.split(",")
            list_skill.extend(skills)
    skill_name_list = []
    skill_count_list = []
    for skill in list_skill:
        if skill in skill_name_list:
            index_of_skill = skill_name_list.index(skill)
            skill_count_list[index_of_skill] += 1
        else:
            skill_name_list.append(skill)
            skill_count_list.append(1)
    # making a list and sort
    sorted_skills = sorted(
        zip(skill_name_list, skill_count_list), key=lambda x: x[1], reverse=True)
    skill_name_list, skill_count_list = map(list, zip(*sorted_skills))
    fig, ax = plt.subplots(figsize=(12, 20))
    color_palette = sns.color_palette("viridis", len(categories))
    sns.barplot(x=skill_count_list[:60],
                y=skill_name_list[:60][::-1],palette=color_palette)
    ax.set_xlabel('Count')
    ax.set_ylabel('Skills')
    ax.set_title('Distribution of Required Skills')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    st.pyplot(fig)


def joblevel():
    job_level = df_selection['job_level'].value_counts()
    job_type = df_selection['job_type'].value_counts()
    colors = sns.color_palette("PuRd", len(job_level))
    colors2 = sns.color_palette("Purples", len(job_level))
    explode = [0.1] + [0] * (len(job_level) - 1)
    explode2 = [0.1] + [0] * (len(job_type) - 1)
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(job_level, labels=job_level.index, autopct='%1.1f%%', startangle=90,
           colors=colors, wedgeprops=dict(width=0.3, edgecolor='w'),
           shadow=True, explode=explode)
    ax.pie(job_type, labels=job_type.index, autopct='%1.1f%%', startangle=90,
           colors=colors2, wedgeprops=dict(width=0.1, edgecolor='w'),
           shadow=True, explode=explode2)
    ax.set_title('Distribution of Job levels and types ')
    st.pyplot(fig)


Home()
job_roles_distribution()
companies_offered_position_distribution()
available_locations()
skillplotter()
joblevel()
