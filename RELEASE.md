# Making a Jupyter Server Release
To create a release, perform the following steps...

## Set up
```
pip install tbump twine build
git pull origin $(git branch --show-current)
git clean -dffx
```

## Update the version and apply the tag
```
echo "Enter new version"
read script_version
tbump ${script_version}
```

## Build the artifacts
```
rm -rf dist
python -m build .
```

## Update the version back to dev
```
echo "Enter dev version"
read dev_version
tbump ${dev_version} --no-tag
```

## Publish the artifacts to pypi
```
twine check dist/*
twine upload dist/*
```
