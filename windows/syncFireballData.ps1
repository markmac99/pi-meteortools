aws s3 sync 2026 s3://ukmda-shared/fireballs/2026/ --exclude "*" --include "2026*" --exclude "*.bz2" --exclude "*nogood*" --profile ukmon-markmcintyre
aws s3 sync 2025 s3://ukmda-shared/fireballs/2025/ --exclude "*" --include "2025*" --exclude "*.bz2" --exclude "*nogood*" --profile ukmon-markmcintyre
aws s3 sync 2024 s3://ukmda-shared/fireballs/2024/ --exclude "*" --include "2024*" --exclude "*.bz2" --exclude "*nogood*" --profile ukmon-markmcintyre
aws s3 sync 2023 s3://ukmda-shared/fireballs/2023/ --exclude "*" --include "2023*"  --exclude "*.bz2" --exclude "*nogood*"  --profile ukmon-markmcintyre
aws s3 sync nonukmon s3://ukmda-shared/fireballs/nonukmon/ --exclude "*" --include "nonukmon" --exclude "*.bz2" --exclude "*nogood*" --profile ukmon-markmcintyre