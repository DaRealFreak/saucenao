# SauceNAO

small script to work with [SauceNAO](https://www.saucenao.com) locally


### Installing
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
from saucenao.saucenao import SauceNao
saucenao = SauceNao('test_directory', api_key='your_api_key')
```

or as application:
```
python usage.py --dir 'test_directory' --api-key='your_api_key'
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