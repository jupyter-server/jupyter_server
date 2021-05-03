# Making a Jupyter Server Release

## Using `jupyter_releaser`

The recommended way to make a release is to use [`jupyter_releaser`](https://github.com/jupyter-server/jupyter_releaser#checklist-for-adoption).

## Manual Release

To create a manual release, perform the following steps:

### Set up

```bash
pip install tbump twine build
git pull origin $(git branch --show-current)
git clean -dffx
```

### Update the version and apply the tag

```bash
echo "Enter new version"
read script_version
tbump ${script_version}
```

### Build the artifacts

```bash
rm -rf dist
python -m build .
```

### Update the version back to dev

```bash
echo "Enter dev version"
read dev_version
tbump ${dev_version} --no-tag
git push origin $(git branch --show-current)
```

### Publish the artifacts to pypi

```bash
twine check dist/*
twine upload dist/*
```
