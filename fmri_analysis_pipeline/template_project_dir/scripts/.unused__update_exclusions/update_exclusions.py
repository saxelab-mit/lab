# update exclusions 

import datetime
import pandas as pd
import sys

subject = sys.argv[1] # subject as 2 digit number in quotes (e.g. '04' or '32')
current_step = sys.argv[2] # current step, based on column names in exclusions.csv
current_step_as_column = 'exclude_from_' + current_step

# get the existing exclusions.csv
df = pd.read_csv('/nese/mit/group/saxelab/projects/EMOfd/data/exclusions.csv')
# get the date and format it 
date = datetime.datetime.now().strftime("%Y%m%d%I%m%S")
# initialize new filename 
filename = '/nese/mit/group/saxelab/projects/EMOfd/scripts/exclusions/previous_exclusion_lists/exclusions' + date + '.csv'

# push contents of old exclusions.csv to new dated filename 
df.to_csv(filename)

# get columns 
col_names = df.columns.tolist()

# figure out which columns to update (starting from where)
col_names_to_update = col_names[col_names.index(current_step_as_column):]

# just turn 0 to 1 to exclude in every column starting with current column  
for colID in col_names_to_update:
	df.loc[df['id'].str.contains(subject), colID] = 1;
		
# write to new exclusions.csv 
df.to_csv('/nese/mit/group/saxelab/projects/EMOfd/data/exclusions.csv', index=False)


