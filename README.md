# SauceNAO

[![Build Status](https://travis-ci.org/DaRealFreak/saucenao.svg?branch=master)](https://travis-ci.org/DaRealFreak/saucenao)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/DaRealFreak/saucenao/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/DaRealFreak/saucenao/?branch=master)
[![Coverage Status](https://coveralls.io/repos/github/DaRealFreak/saucenao/badge.svg?branch=master)](https://coveralls.io/github/DaRealFreak/saucenao?branch=master)

small script to work with [SauceNAO](https://www.saucenao.com) locally


### Installing
This script runs with [Python 3](https://www.python.org).
There is a currently working [Python 2 branch](https://github.com/DaRealFreak/saucenao/tree/Python-2.x), but I'm not going to update it anymore.

Download this repository and run the setup.py to install all necessary dependencies

### Dependencies


Required:

* [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup) - html parser
* [requests](https://github.com/requests/requests) - http library

Optional:

* [Pillow](https://python-pillow.org) - Python Imaging Library, used to generate images for unittests
* [python-dotenv](https://github.com/theskumar/python-dotenv) - .env file loader used for unittests


### Usage
You can run SauceNAO either as module:
```
import logging
from saucenao.saucenao import SauceNao

saucenao = SauceNao('directory', databases=999, minimum_similarity=65, combine_api_types=False, api_key='',
                    exclude_categories='', move_to_categories=False, output_type=SauceNao.API_HTML_TYPE, start_file='',
                    log_level=logging.ERROR, title_minimum_similarity=90)

```

or as application:
```
python usage.py --dir [--databases] [--minimum-similarity] [--combine-api-types] [--api-key] [--exclude-categories] [--move-to-categories] [--output-type] [--start-file] [--log-level] [--filter-creation-date] [--filter-modified-date] [--title-minimum-similarity]
```

you can also use it to get the gathered information for your own script:
```
filtered_results = saucenao.check_file('test.jpg')
```
or get a generator object for a bulk of files:
```
results = saucenao.check_files(('test.jpg', 'test2.jpg'))
```


## Running the tests

In the tests folder you can run each unittest individually.

The test cases should be self-explanatory.


## Development
Want to contribute? Great!

I'm always glad hearing about bugs or pull requests.


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details


## Thanks

A big thanks to [SauceNAO](https://www.saucenao.com) who are indexing all the images and compare them.
This script would be completely useless without them.