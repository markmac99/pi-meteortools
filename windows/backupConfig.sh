#!/bin/bash
# Copyright (C) Mark McIntyre

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
pushd $here
cd /mnt/c/Users/$USER/OneDrive/dev/meteorcam_config

rsync -avz --include-from ./rms.txt --exclude "*" uk0006:source/Stations/UK0006/ ./uk0006
rsync -avz --include-from ./rms.txt --exclude "*" uk000f:source/Stations/UK000F/ ./uk000f
rsync -avz --include-from ./rms.txt --exclude "*" uk001l:source/Stations/UK001L/ ./uk001l
rsync -avz --include-from ./rms.txt --exclude "*" uk002f:source/Stations/UK002F/ ./uk002f
rsync -avz  uk0006:.ssh/ ./uk0006/ssh
rsync -avz  uk000f:.ssh/ ./uk000f/ssh
rsync -avz  uk001l:.ssh/ ./uk001l/ssh
rsync -avz  uk002f:.ssh/ ./uk002f/ssh
rsync -avz --include-from ./ukmon.txt --exclude "*" uk0006:source/ukmon-pitools-UK0006/ ./uk0006/ukmon
rsync -avz --include-from ./ukmon.txt --exclude "*" uk000f:source/ukmon-pitools-UK0006/ ./uk000f/ukmon
rsync -avz --include-from ./ukmon.txt --exclude "*" uk001l:source/ukmon-pitools-UK001L/ ./uk001l/ukmon
rsync -avz --include-from ./ukmon.txt --exclude "*" uk002f:source/ukmon-pitools-UK002F/ ./uk002f/ukmon

rsync -avz --include-from ./tackley.txt --exclude "*" uk0006:source/tackley-tools/ ./uk0006/tackley
rsync -avz --include-from ./tackley.txt --exclude "*" uk000f:source/tackley-tools/ ./uk000f/tackley
rsync -avz --include-from ./tackley.txt --exclude "*" uk001l:source/tackley-tools/ ./uk001l/tackley
rsync -avz --include-from ./tackley.txt --exclude "*" uk002f:source/tackley-tools/ ./uk002f/tackley
popd
