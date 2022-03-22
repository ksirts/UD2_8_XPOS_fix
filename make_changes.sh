#!/bin bash

# Path to UD2_8 dir
DATA_DIR=$HOME/Data/UD2_8/

python3 make_changes.py --data_dir $DATA_DIR/Train --output_dir $DATA_DIR/Train_fix --changes_fn UD_XPOS_fixes_train.tsv
python3 make_changes.py --data_dir $DATA_DIR/Dev --output_dir $DATA_DIR/Dev_fix --changes_fn UD_XPOS_fixes_dev.tsv
python3 make_changes.py --data_dir $DATA_DIR/Test --output_dir $DATA_DIR/Test_fix --changes_fn UD_XPOS_fixes_test.tsv
