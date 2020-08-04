
To create a release, run the following:

```
git clean -dfx
python setup.py sdist
python setup.py bdist_wheel
script_version=`python setup.py --version 2>/dev/null`
git commit -a -m "Release $script_version"
git tag $script_version
git push --all
git push --tags
pip install twine
twine check dist/* 
twine upload dist/*
```
