# SauceNAO
![tests](https://github.com/DaRealFreak/saucenao/workflows/tests/badge.svg?branch=master)
[![Coverage Status](https://coveralls.io/repos/github/DaRealFreak/saucenao/badge.svg?branch=master)](https://coveralls.io/github/DaRealFreak/saucenao?branch=master)
![GitHub](https://img.shields.io/github/license/DaRealFreak/saucenao)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/DaRealFreak/saucenao/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/DaRealFreak/saucenao/?branch=master)  
unofficial python module to make working with [SauceNAO](https://www.saucenao.com) in projects easier

## Installation
This package requires [Python](https://www.python.org) 3.6 or later.  

You can simply install the latest version with
```shell script
pip install SauceNAO
```

Alternatively you can download this repository and run the setup.py to install all necessary dependencies.
In case you want to install the dependencies to run the unit tests you can additionally run `pip install -e .[dev]` in this project.

## Dependencies
Required:
 * [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup) - html parser
 * [requests](https://github.com/requests/requests) - http library

Optional:
 * [Pillow](https://python-pillow.org) - Python Imaging Library, used to generate images for unittests
 * [python-dotenv](https://github.com/theskumar/python-dotenv) - .env file loader used for unittests
 * [requests-mock](https://pypi.python.org/pypi/requests-mock) - requests mock responses used for unittests

## Usage
You can run SauceNAO either as module:
```
import logging

from saucenao import SauceNao, SauceNaoDatabase

saucenao = SauceNao(directory='directory', databases=SauceNaoDatabase.All, minimum_similarity=65,
                    combine_api_types=False, api_key='', is_premium=False, exclude_categories='',
                    move_to_categories=False, use_author_as_category=False, output_type=SauceNao.API_HTML_TYPE,
                    start_file='', log_level=logging.ERROR, title_minimum_similarity=90)
```

or as application:
```
python usage.py --dir [--databases] [--minimum-similarity] [--combine-api-types] [--api-key] [--premium]
                [--exclude-categories] [--move-to-categories] [--use-author-as-category] [--output-type] [--start-file]
                [--log-level] [--filter-creation-date] [--filter-modified-date] [--title-minimum-similarity]
```

you can also use it to get the gathered information for your own script:
```
filtered_results = saucenao.check_file(file_name='test.jpg')
```

or get a generator object for a bulk of files using the worker class, all parameters work here too:
```
from saucenao import Worker

results = Worker(directory='directory', files=('test.jpg', 'test2.jpg')).run()
```

## Running the tests
In the tests folder you can run each unittest individually.  
The test cases should be self-explanatory.

## Development
Want to contribute? Great!  
I'm always glad hearing about bugs or pull requests.

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE) file for details

## Thanks
A big thanks to [SauceNAO](https://www.saucenao.com) who are indexing all the images and compares them.  
This script would be completely useless without them.