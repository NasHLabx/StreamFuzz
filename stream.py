import logging
import os
import asyncio
import aiohttp
from aiohttp import ClientSession
import json

# Configurations
DEFAULT_WORDLIST = 'Wordlist/pro_100.txt'
DEFAULT_OUTPUT = 'results.txt'
DEFAULT_HEADERS = {}
DEFAULT_COOKIES = {}
VALID_STATUS_CODES = list(range(200, 300)) + [401, 403]
DEFAULT_METHODS = ['HEAD']
MAX_CONCURRENT_REQUESTS = 100  # Rate limiting
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
COMMON_PATHS = ['/admin', '/login', '/dashboard', '/user', '/api']

# Setup logger
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger('StreamFuzz')

# Color ANSI escape codes
class Color:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class StreamFuzz:
    def __init__(self, base_url, wordlist, output_file, headers, cookies, methods, valid_status_codes):
        self.base_url = base_url.rstrip('/')
        self.wordlist = wordlist
        self.output_file = output_file
        self.headers = headers
        self.cookies = cookies
        self.methods = methods
        self.valid_status_codes = valid_status_codes
        self.found_endpoints = set()
        self.session = None

    async def _fetch(self, path, method):
        """Perform an HTTP request."""
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            async with self.session.request(method, url, headers=self.headers, cookies=self.cookies) as response:
                if response.status in self.valid_status_codes:
                    logger.info(f"{Color.OKGREEN}[{response.status}] {url}{Color.ENDC}")
                    self.found_endpoints.add(url)
                return response.status
        except Exception as e:
            logger.error(f"{Color.FAIL}Error fetching {url}: {e}{Color.ENDC}")

    async def _process_paths(self, paths):
        """Process paths asynchronously."""
        sem = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)  # Rate limiting
        tasks = []

        async def _bound_fetch(path, method):
            async with sem:
                await self._fetch(path, method)

        for path in paths:
            for method in self.methods:
                tasks.append(_bound_fetch(path, method))
        await asyncio.gather(*tasks)

    async def _load_wordlist(self):
        """Load paths from the wordlist."""
        paths = []
        if os.path.exists(self.wordlist):
            with open(self.wordlist, 'r') as file:
                paths.extend([line.strip() for line in file if line.strip()])
        # Auto-detect common paths if not in the wordlist
        paths.extend(COMMON_PATHS)
        return list(set(paths))  # Ensure unique paths

    async def start(self):
        """Start fuzzing."""
        paths = await self._load_wordlist()
        logger.info(f"Loaded {len(paths)} paths from the wordlist.")
        async with ClientSession() as session:
            self.session = session
            await self._process_paths(paths)
            self._save_results()

    def _save_results(self):
        """Save discovered endpoints to the output file."""
        if not self.found_endpoints:
            logger.warning(f"{Color.WARNING}No endpoints discovered.{Color.ENDC}")
            return
        with open(self.output_file, 'w') as file:
            for endpoint in sorted(self.found_endpoints):
                file.write(f"{endpoint}\n")
        logger.info(f"Results saved to '{self.output_file}'.")


def display_welcome_screen():
    """Display the welcome screen."""
    print(f"{Color.HEADER}=" * 50)
    print(f"       {Color.OKBLUE}Welcome to NasHLabs StreamFuzz{Color.ENDC}")
    print(f"          {Color.OKGREEN}Discover Hidden Endpoints{Color.ENDC}")
    print(f"{Color.HEADER}=" * 50)
    print(f"\n{Color.BOLD}Options:{Color.ENDC}")
    print(f"1. Start fuzzing")
    print(f"2. Set configurations (URL, wordlist, output file, etc.)")
    print(f"3. View current configurations")
    print(f"4. Exit")
    print(f"{Color.HEADER}=" * 50)


def interactive_menu():
    """Interactive menu for user input."""
    base_url = None
    wordlist = DEFAULT_WORDLIST
    output_file = DEFAULT_OUTPUT
    headers = DEFAULT_HEADERS
    cookies = DEFAULT_COOKIES
    methods = DEFAULT_METHODS
    valid_status_codes = VALID_STATUS_CODES

    while True:
        display_welcome_screen()
        choice = input(f"{Color.OKBLUE}Select an option: {Color.ENDC}").strip()

        if choice == '1':  # Start fuzzing
            if not base_url:
                print(f"{Color.FAIL}Please set the target URL in the configurations first.{Color.ENDC}")
                continue
            print(f"\n{Color.OKGREEN}Starting fuzzing...{Color.ENDC}")
            fuzzer = StreamFuzz(
                base_url=base_url,
                wordlist=wordlist,
                output_file=output_file,
                headers=headers,
                cookies=cookies,
                methods=methods,
                valid_status_codes=valid_status_codes
            )
            asyncio.run(fuzzer.start())

        elif choice == '2':  # Set configurations
            print(f"\n{Color.OKBLUE}Set Configurations:{Color.ENDC}")
            base_url = input(f"Enter target URL [{base_url or 'Not set'}]: ").strip() or base_url
            wordlist = input(f"Enter wordlist file path [{wordlist}]: ").strip() or wordlist
            output_file = input(f"Enter output file path [{output_file}]: ").strip() or output_file
            headers_input = input("Enter custom headers as JSON (leave blank for none): ").strip()
            if headers_input:
                headers = json.loads(headers_input)
            cookies_input = input("Enter custom cookies as JSON (leave blank for none): ").strip()
            if cookies_input:
                cookies = json.loads(cookies_input)
            methods_input = input(f"Enter HTTP methods as comma-separated values [{','.join(methods)}]: ").strip()
            if methods_input:
                methods = methods_input.split(',')
            status_codes_input = input(f"Enter valid status codes as comma-separated values [{','.join(map(str, valid_status_codes))}]: ").strip()
            if status_codes_input:
                valid_status_codes = list(map(int, status_codes_input.split(',')))
            print(f"{Color.OKGREEN}Configurations updated.{Color.ENDC}")

        elif choice == '3':  # View current configurations
            print(f"\n{Color.OKBLUE}Current Configurations:{Color.ENDC}")
            print(f"Target URL: {base_url or 'Not set'}")
            print(f"Wordlist File: {wordlist}")
            print(f"Output File: {output_file}")
            print(f"Headers: {json.dumps(headers, indent=2)}")
            print(f"Cookies: {json.dumps(cookies, indent=2)}")
            print(f"HTTP Methods: {', '.join(methods)}")
            print(f"Valid Status Codes: {', '.join(map(str, valid_status_codes))}")
            input(f"\n{Color.OKGREEN}Press Enter to return to the main menu...{Color.ENDC}")

        elif choice == '4':  # Exit
            print(f"{Color.FAIL}Exiting the program. Goodbye!{Color.ENDC}")
            break

        else:
            print(f"{Color.FAIL}Invalid choice. Please try again.{Color.ENDC}\n")


if __name__ == '__main__':
    interactive_menu()
