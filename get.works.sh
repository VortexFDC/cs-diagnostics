#!/bin/bash

# This script is used to get intermediate files from a run

# Create a function to get the intermediate files
get_work_data() {
    local work_id=$1
    local stage=${2:-"all"}
    local include_derived=${3:-"false"}

    echo "Getting intermediate files for work_id: $work_id and stage: $stage"

    newnum=`echo $work_id | awk '{printf "%04i\n", int($1/1000)}'`
    run_path=server-1:/home/vortex/runs/$newnum/$work_id/
    mkdir -p data/$work_id/out/

    if [ "$stage" == "all" ]; then
        get_work_data $work_id "obs" $include_derived
        get_work_data $work_id "new" $include_derived
        get_work_data $work_id "extend" $include_derived
    elif [ "$stage" == "obs" ]; then
        mkdir -p data/$work_id/out/ts/$stage
        rsync -avzO $run_path/out/ts/$stage/*nc data/$work_id/out/ts/$stage
        if [ "$include_derived" == "true" ]; then
            mkdir -p data/$work_id/out/ts/$stage/derived/
            rsync -avzO $run_path/out/ts/$stage/derived/*nc data/$work_id/out/$stage/derived/
        fi
    elif [ "$stage" == "extend" ]; then
        mkdir -p data/$work_id/out/ts/$stage
        rsync -avzO $run_path/out/ts/$stage/*nc data/$work_id/out/ts/$stage
        if [ "$include_derived" == "true" ]; then
            echo "No derived files for stage: $stage"
        fi
    elif [ "$stage" == "new" ]; then
        mkdir -p data/$work_id/out/$stage/essential/
        rsync -avzO $run_path/out/$stage/essential/ data/$work_id/out/$stage/essential/
        if [ "$include_derived" == "true" ]; then
            mkdir -p data/$work_id/out/$stage/derived/
            rsync -avzO $run_path/out/$stage/derived/ data/$work_id/out/$stage/derived/
        fi
    fi
}

# Path to the CSV file
csv_file="works.csv"

# Read the CSV file line by line
while IFS=, read -r run_id work_id; do

    # Process each line
    # If data/$work_id/out exists, skip
    if [ -d "data/$work_id/out" ]; then
        echo "Skipping work_id: $work_id"
        continue
    fi

    echo "Processing run_id: $run_id, work_id: $work_id"
    get_work_data $work_id "all" "false"

done < "$csv_file"
