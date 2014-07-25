# BC Libraries Web Page Crawler

This crawls Boston College Libraries' web pages

## Requirements

* [Scrapy](http://doc.scrapy.org/en/latest/) Web Crawler

## Installation

See [Scrapy Installation Guide](http://doc.scrapy.org/en/latest/intro/install.html)

## Running the Crawler

After installing [Scrapy](http://doc.scrapy.org/en/latest/) and downloading the files in this repo, enter the following
into the command line interface:

    scrapy crawl LibServices -o libweb.json -t json

`-o file` 	indicates the output file
`-t file_type` 	indicates the format of the output, e.g. json, csv, etc.

## TODO

* Ignore Javascript/CSS markup
* Move text processing into Pipeline
* Change name of crawler (LibServices?? -> BCLibWeb)

