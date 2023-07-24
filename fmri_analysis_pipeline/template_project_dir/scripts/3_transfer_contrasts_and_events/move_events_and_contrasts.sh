study_root=`cat ../PATHS.txt`

datadir=$study_root/data

eventfiles="$datadir/event_files"

con_file_name=contrasts.tsv
contrastfile="$datadir/contrast_files/$con_file_name"

BIDSdir=$datadir/BIDS

##################################

# move contrasts file to BIDS dir

bids_contrastdir="$BIDSdir/code"
# if it doesn't already exist, make it
if [[ ! -e $bids_contrastdir ]]; then mkdir $bids_contrastdir; else echo "BIDS contrast dir already exists"; fi

#copy to contrastdir 
echo "------------------------"
echo "syncing contrast file"
echo "------------------------"
rsync -av $contrastfile $bids_contrastdir/$con_file_name


###################################

# find subjects and sync events files to BIDS dir 

find $eventfiles/ -type d -name "sub*" -exec realpath --relative-to $eventfiles {} \;|while read dname; do
  echo "------------------------"
  echo "syncing files for $dname"
  echo "------------------------"
  rsync -av $eventfiles/$dname/sub-*.tsv $BIDSdir/$dname/func/
done

