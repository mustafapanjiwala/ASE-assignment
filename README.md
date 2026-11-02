# ASE Entry Test – "Will it install on Python 3.11?"

`check_requirements.py` checks every line of a `requirements.txt` against the PyPI JSON API and reports:

1. **Dependencies checked** – number of (non-empty) lines in the file
2. **Not found on PyPI** – package or pinned version does not exist (404)
3. **Incompatible with Python 3.11** – release's `requires_python` excludes 3.11 (upper bounds included); no `requires_python` counts as compatible
4. **Highest requirement** – the release whose `requires_python` has the highest minimum Python version

## Usage

```bash
pip install requests packaging
python check_requirements.py requirements.txt
```

## Results

Sample input (`sample_requirements.txt`):

```
Dependencies checked: 5
Not found on PyPI: 1
Incompatible with Python 3.11: 2
Highest requirement: django==6.0 (>=3.12)
```

Task input (`requirements.txt`):

```
Dependencies checked: 8
Not found on PyPI: 2
Incompatible with Python 3.11: 1
Highest requirement: numpy==2.3.0 (>=3.11)
```

- Not found: `fastapi-agent-router` (package doesn't exist), `matplotlib==3.99.0` (version doesn't exist)
- Incompatible: `scipy==1.7.0` (`>=3.7,<3.10`)
