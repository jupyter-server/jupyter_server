# Making a Jupyter Server Release
To create a release, perform the following steps...

## Remove untracked files
```
git clean -dffx
```

## Update the version and apply the tag
```
vim jupyter_server/_version.py
export script_version=`python setup.py --version 2>/dev/null`
git commit -a -m "Release $script_version"
git tag $script_version
```

## Build the artifacts
```
rm -rf dist
python setup.py sdist
python setup.py bdist_wheel
```

## Update the version back to dev
```
vim jupyter_server/_version.py
git commit -a -m "Back to dev version"
```

## Push the commits and tag
```
git push --all
git push --tags
```

## Publish the artifacts to pypi
```
pip install twine
twine check dist/* 
twine upload dist/*
```
