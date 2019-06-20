import asyncio
import logging
import re
import aiohttp
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from datetime import datetime

#setup logging
logger = logging.getLogger('crawling_result')
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('keyword_top_video_result.log')
file_handler.setLevel(logging.INFO)
log_formatter = logging.Formatter(fmt='%(message)s')
file_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)

# upload date -> Today / type -> video / sort by -> view count
BASE_URL = "https://www.youtube.com/results?search_query={}&sp=CAMSBAgCEAE=3D"


# async request
async def fetch_request(_url: str, _session: ClientSession) -> BeautifulSoup:
    try:
        resp = await _session.request(method="GET", url=_url)
        resp.raise_for_status()
        html = await resp.text()
        return BeautifulSoup(html, 'lxml')
    except asyncio.TimeoutError:
        logger.error('Can not open url=%s, occured=TimeoutError', _url)
        return None


async def top_video_parser(_url: str, _session: ClientSession) -> None:
    try:
        bsoup = await fetch_request(_url, _session)
    except (aiohttp.ClientError, aiohttp.http_exceptions.HttpProcessingError,) as e:
        logger.error("aiohttp exception for %s", e)
        return None
    else:
        a_founds = bsoup.findAll('a', {"class": "yt-uix-sessionlink spf-link"})
        for _a in a_founds:
            _a_str = _a['href']
            # if re.match('/channel', _a_str):
            #     logger.info(_a_str)
            if re.match('/watch', _a_str):
                logger.info("https://www.youtube.com/{}".format(_a_str))


async def bulk_top_video(_keywords: dict) -> None:
    async with ClientSession() as _session:
        top_video_tasks = []
        for keyword in _keywords:
            _url = BASE_URL.format(keyword)
            top_video_tasks.append(
                top_video_parser(_url, _session)
            )
        await asyncio.gather(*top_video_tasks)


if __name__ == '__main__':
    keywords = [
        'cryptocurrency',
    ]
    try:
        top_video_loop = asyncio.get_event_loop()
        top_video_loop.run_until_complete(bulk_top_video(keywords))
        top_video_loop.close()
    except (KeyboardInterrupt, SystemExit):
        logger.error('KeyboardInterrupt or SystemExit: {}'.format(datetime.now()))

