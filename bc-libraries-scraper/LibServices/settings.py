# Scrapy settings for LibServices project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
# http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'LibServices'

SPIDER_MODULES = ['LibServices.spiders']
NEWSPIDER_MODULE = 'LibServices.spiders'
RETRY_TIMES = 0

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'LibServices (+http://www.yourdomain.com)'
