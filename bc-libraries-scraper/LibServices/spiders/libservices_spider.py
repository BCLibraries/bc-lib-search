from scrapy.contrib.spiders import Rule, CrawlSpider
from scrapy.selector import Selector
from LibServices.items import LibservicesItem
from scrapy.http.request import Request
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
import re


class LibServicesSpider(CrawlSpider):
    name = "LibServices"
    allowed_domains = ["bc.edu"]
    start_urls = ["http://bc.edu/libraries"]
    seen = set()

    rules = (Rule(SgmlLinkExtractor(allow=("/libraries/.*",)), callback="parse_url", follow=True),)

    def parse_url(self, response):
        # extract links
        for n, rule in enumerate(self.rules):
            links = [l for l in rule.link_extractor.extract_links(response) if l not in self.seen]
            if links and rule.process_links:
                links = rule.process_links(links)
            self.seen = self.seen.union(links)
            for link in links:
                r = Request(url=link.url, callback=self.parse_url)
                r.meta.update(rule=n, link_text=link.text)  # store page's href text
                r.meta.update(rule=n, link=response.url)  # store page's "parent"
                yield rule.process_request(r)

        # process reponse
        yield self.process_data(response)

    def process_data(self, response):
        sel = Selector(response)
        item = LibservicesItem()

        if "link_text" in response.meta and "link" in response.meta:
            item["hrefTitle"] = self.makeTitle(response.meta["link_text"])
            item["refURL"] = response.meta["link"]

        item["title"] = sel.xpath('//title/text()').extract()[0]
        item["url"] = response.url
        item["text"] = self.merge_text(sel.xpath('//text()').extract())
        return item

    catchWords = ["function", "font-family", "/*", "var", "}"]  # look into scrapy remove markup modules

    def merge_text(self, textList):
        temp = []
        for txt in textList:
            if not txt.isspace() and True not in [c in txt for c in self.catchWords]:
                temp.append(' '.join(txt.split()))
        return ' '.join(temp).lower()

    def makeTitle(self, s):
        """ capitalizes first letter of every word """
        s = ' '.join(s.split())
        return re.sub(r"[A-Za-z]+('[A-Za-z]+)?", lambda mo: mo.group(0)[0].upper() + mo.group(0)[1:].lower(), s)
