# Release

## To release a new version of Nutmeg on PyPI:

```bash
git add <any new stuff>
git commit -a

python setup.py sdist upload
python setup.py bdist_wheel upload

git tag -a X.X.X -m 'comment'
```

Update _version.py (add 'dev' and increment minor) and then:

```bash
git commit -a

git push
git push --tags
```
