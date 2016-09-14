git pull
pushd ../mozilla-central/ && hg pull && hg update
popd
python generate.py
git commit -m "daily changes" -a
git push
