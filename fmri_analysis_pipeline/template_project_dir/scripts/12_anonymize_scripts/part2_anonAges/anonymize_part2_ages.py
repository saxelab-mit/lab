import pandas as pd
import random
import sys
import os.path as op
import re

# usage: singularity exec -B /om:/om -B /om3:/om3 -B /mindhive:/mindhive /om3/group/saxelab/$proj/singularity_images/anonymize.sif python anonymize_part2_ages.py $proj

proj_dir = sys.argv[1]
participants_tsv_path = op.join(proj_dir, "data/BIDS_anon/participants.tsv")

df = pd.read_csv(participants_tsv_path, sep="\t")

# Print out ages before
print("ages before:", df['age'].tolist())

# Iterate through df, (per participant) if we find an odd age, randomly increment or decrement it
d = {}
for i, row in df.iterrows():
    if df.at[i, 'age'] % 2 != 0: # if odd
        key = df.at[i, 'participant_id']
        # make key = subject
        mo = re.match('.+([0-9])[^0-9]*$', key)
        key = key[:(mo.start(1)+1)]
        if key in d:
            df.at[i, 'age'] = d[key]
        else:
            df.at[i, 'age'] += random.choice([1, -1])
            d[key] = df.at[i, 'age']

# Show that we only have even ages now
print("ages after:", df['age'].tolist())

# Output the anonymized file
df.to_csv(participants_tsv_path, sep="\t", index=False)
                      
