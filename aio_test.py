"""
async spider

"""
import asyncio
import threading
import time
import requests
import re, os
from aiofile import async_open
import aiohttp

class BaseIO:
    def __init__(self, _output_dir, _reg):
        self._output_dir = _output_dir
        self._reg = _reg

    def _get_sync(self, url):
        response = requests.request("get", url=url)
        return response

    async def _get_async(self, url):
        async with aiohttp.ClientSession() as session:
            response = await session.get(url)
            content = await response.read()
        return content
    
    def _check_path(self, rel_path):
        download_path = os.path.join(self._output_dir, rel_path)
        download_dir = os.path.dirname(download_path)
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        return download_path
    
    def _download_sync(self, content, rel_path):
        download_path = self._check_path(rel_path)
        with open(download_path, "wb+") as f:
            f.write(content)
    
    async def _download_async(self, content, rel_path):
        download_path = self._check_path(rel_path)
        async with async_open(download_path, 'wb+') as af:
            await af.write(content)
            af.seek(0)

class SpiderSync(BaseIO):
    
    def _step_crawl(self, url, dirname):
        response = self._get_sync(url)
        match_patterns = re.findall(self._reg, response.text)

        for index, re_url in enumerate(match_patterns):
            rel_path = "{}/{}".format(dirname, re_url.split("/")[-1])

            pattern_response = self._get_sync(re_url)
            self._download_sync(pattern_response.content, rel_path)

    def run(self, spider_urls):
         for index, url in enumerate(spider_urls):
            self._step_crawl(url, str(index))

class SpiderCoroutine(BaseIO):

    async def _step_crawl(self, re_url, rel_path):
        content = await self._get_async(re_url)
        await self._download_async(content, rel_path)

    async def run(self, spider_urls):
        coroutine_list = []
        for index, url in enumerate(spider_urls):
        
            response = self._get_sync(url)
            match_patterns = re.findall(self._reg, response.text)
            
            for re_url in match_patterns:
                rel_path = "{}/{}".format(str(index), re_url.split("/")[-1])
                coroutine_list.append(self._step_crawl(re_url, rel_path))

        await asyncio.gather(*coroutine_list)

class SpiderThreads(SpiderSync):

    def run(self, spider_urls):
        thread_list = []
        for index, url in enumerate(spider_urls):
            t = threading.Thread(target=self._step_crawl, args=(url, str(index)))
            thread_list.append(t)
            t.start()
        
        for i in thread_list:
            i.join()

class SpiderFactory:
    output = ""
    reg = ""
    url = []
    
    def get_spider_threads(self):
        return SpiderThreads(self.output, self.reg)

    def get_spider_sync(self):
        return SpiderSync(self.output, self.reg)

    def get_spider_asyncio(self):
        return SpiderCoroutine(self.output, self.reg)


class DemoSpider(SpiderFactory):
    
    spider_urls = [
        "http://www.ikmt.net/mntp/xgmn",
        "http://www.ikmt.net/mntp/qcmn",
        "http://www.ikmt.net/mntp/mnxh",
        "http://www.ikmt.net/mntp/xgcm"
    ]
    output = r'D:\temp\spider'
    reg = r'<img src="(http:\/\/www\.ikmt\.net.*?\.jpg)"' 

if __name__ == "__main__":

    start_tm = time.time()
    
    spider = DemoSpider()
    spider_urls = spider.spider_urls

    # # sync
    # spider.get_spider_sync().run(spider_urls)

    # threads
    spider.get_spider_threads().run(spider_urls)

    # # asyncio
    # asyncio.run(spider.get_spider_asyncio().run(spider_urls))

    print("I am rebase")
    print(" I am dev")
    print(" i am master")
    print("================cost time is:", (time.time() - start_tm))
