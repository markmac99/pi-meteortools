#!/bin/bash

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
pushd $here
rsync -avz uk0006:RMS_data/ArchivedFiles/*/*ff_intervals.png ../ff_intervals/uk0006
rsync -avz uk000f:RMS_data/ArchivedFiles/*/*ff_intervals.png ../ff_intervals/uk000f
rsync -avz uk002f:RMS_data/ArchivedFiles/*/*ff_intervals.png ../ff_intervals/uk002f
rsync -avz uk001l:RMS_data/ArchivedFiles/*/*ff_intervals.png ../ff_intervals/uk001l
popd
