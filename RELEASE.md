# Making a Jupyter Server Release

## Using `jupyter_releaser`

The recommended way to make a release is to use [`jupyter_releaser`](https://github.com/jupyter-server/jupyter_releaser#checklist-for-adoption).

Note that we must use manual versions since Jupyter Releaser does not
yet support "next" or "patch" when dev versions are used.

## Manual Release

To create a manual release, perform the following steps:

### Set up

```bash
pip install hatchling twine build
git pull origin $(git branch --show-current)
git clean -dffx
npm install
npm run build
```

### Update the version and apply the tag

```bash
echo "Enter new version"
read new_version
hatchling version ${new_version}
git tag -a ${new_version} -m "Release ${new_version}"
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
hatchling version ${dev_version}
git push origin $(git branch --show-current)
```

### Publish the artifacts to pypi

```bash
twine check dist/*
twine upload dist/*
```
