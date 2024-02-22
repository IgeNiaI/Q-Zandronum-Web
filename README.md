# Q-Zandronum-Web
Django website for Q-Zandronum project.

## Installation
**Reguirements**
Project is using python poetry package and environment manager, use it to install python dependecies, see pyproject.toml
- **python** >= 3.8.5
- **poetry**
- **Nginx**
- **PostgreSQL** >= 10 *(could be swapped for another DBMS, but PG is highly recommended)*
```bash
$ poetry shell
$ poetry install
$ python manage.py check
```

### Isues with poetry
If it hangs or errors out it might be because of it's strange keyring usage.
Try env var `PYTHON_KEYRING_BACKEND=keyring.backends.fail.Keyring`

## Upgrading packages
On local repo:
```bash
$ poetry update
```
Resolves dependecies based on `pyproject.toml` and installs them. Commit `poetry.lock` and push it.

On remote repo:
```bash
$ poetry install
```
Will use `poetry.lock` to install exact versions of packages.

## Configuration
### settings.py file
> some settings are read from environment variables, see uWSGI service file.

 - CELESTIA_ALLOWED_NESTED_EXTS - add allowed nested extensions for file uploads. e.g. ('tar', 'ext') to save .tar.gz or .ext.zip extension in file name.
### qzandronum.ini
Configuration file for app server (uWSGI by default)


## Page Configuration
Meta like page description, page title and keywords can be set through PageConfig admin
