from data_portal import Arlington
import pandas as pd

arva = Arlington()
frame = arva.police_incidents(1000)

working_data = pd.DataFrame.copy(frame) # Make a copy of the 'frame' for a new dataset

date_time_col_to_fix = ["firstReportDtm", "lastReportDtm"] # Making these into datetime data types
for column in date_time_col_to_fix:
    working_data[column] = working_data[column].str.replace("T", " ")
    working_data[column] = pd.to_datetime(working_data[column])

lat_long_col_to_fix = ["latitudeCrd", "longitudeCrd"] #Making these into float
for column in lat_long_col_to_fix:
    working_data[column] = working_data[column].astype(float)

crimes = { #Making a dict of regexes to use and the general category they belong in.
    "PROPERTY" : ["PROPERTY", "DEFACE", "DESTROY", "TRESPAS",
                "ARSON", "VANDAL"],
    "THEFT" : ["SHOPLIFT", "LARCENY", "FRAUD", "THEFT", "BURGLAR",
             "EMBEZZLE", "ROB", "STOLEN", "EXTORT", "COUNTERFEIT",
             "OBTAIN.* MONEY .* FALSE PRETENSE"],
    "ALCOHOL" : ["ALCOHOL", "DRUNK", "DUI", "INTOXICAT"],
    "DRUGS" : ["DRUGS?", "MARIJUANA", "CONTROL.{0,3} SUBSTANCE",
               "POSSESSION OF SCHEDULE"],
    "HIT_AND_RUN" : ["HIT AND RUN"],
    "VIOLENT" : ["ASSAULT", "BATTERY", "FIREARM", "WEAPON", "WOUNDING", "SHOOT",
               "STRANGULATION", "STALK", "THREAT"]
}

#FYI:
for category in crimes:
    for crime in crimes[category]:
        print(category, " includes ", crime)

# FUCK YES

# This makes a column for each category of crimes for each row in working_data. Flag the corresponding cell and column with the column
# name if there is a match, otherwise puts "X". Will combine all columns into one for graphing and mapping purposes

import re
match_list = []
iteration_num = 0
current_row = 0

for category in crimes:
    for crime in crimes[category]:
        for row in working_data.offenseDsc:
            if re.search(crime, row, re.IGNORECASE) is not None:
                match = category
            else:
                match = "X"
            if iteration_num == 0:
                match_list.append(match)
                current_row += 1
            elif match == "X":
                current_row += 1
                continue
            else:
                match_list[current_row] = match
                current_row += 1
        else:
            iteration_num += 1
            current_row = 0
    else:
        working_data[category] = match_list
        match_list = []
        if iteration_num != 1:
            print(iteration_num, " iterations completed for ", category)
        else:
            print(iteration_num, " iteration completed for ", category)
        iteration_num = 0
working_data.loc[:, ["offenseDsc", "PROPERTY", "THEFT", "ALCOHOL", "DRUGS", "HARASS", "HIT_AND_RUN", "VIOLENT"]]


#Next piece:
pd.set_option('max_rows', 100)

working_data["LEADER"] = "OTHER" # default
crime_columns = list(crimes.keys())

#Choose the leading crime category in that ascending order and make a column with that one category
for row in range(len(working_data)):
    for column in crime_columns:
        if working_data.loc[row, column] != "X":
            working_data.loc[row, "LEADER"] = column #Change the value in the Leader column to any crime
            # where the match is not "X'. Because of the order, the later column matches will overwrite the former ones.
            continue

#Move the offensceDsc next to flags for easier viewing
column_order = list(working_data.columns)
column_order.remove("offenseDsc")
column_order.insert(column_order.index("PROPERTY"), "offenseDsc")
working_data = working_data.loc[:, column_order]


# This section is where I started to explore graphing. I'm not sure of the graphing utility I/We will use, but my
# explorations of plotnine and knowledge of ggplot made me think it needed to be in DataFrame form. We can discuss.

import numpy as np
grouped = working_data.groupby("LEADER")
group_counts = grouped["LEADER"].count()
group_counts_df = pd.DataFrame({'Category':group_counts.index, 'Count':group_counts.values}).\
    sort_values(by="Count", ascending=False).\
    reset_index(drop=True)

order = group_counts_df["Category"]

group_counts_df.Category = pd.Categorical(group_counts_df["Category"], categories=order, ordered=True)