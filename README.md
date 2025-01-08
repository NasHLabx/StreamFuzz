# StreamFuzz

StreamFuzz is a Python-based fuzzing tool designed to discover hidden endpoints on web applications. It uses asynchronous HTTP requests to efficiently test a large number of paths with customizable configurations.

## Features

- **Asynchronous Requests**: Fast fuzzing using `aiohttp` for handling multiple requests concurrently.
- **Customizable Configurations**: Modify target URL, wordlists, headers, cookies, HTTP methods, and valid status codes.
- **Rate Limiting**: Control the maximum number of concurrent requests.
- **Results Storage**: Automatically save discovered endpoints to a file.
- **Interactive Menu**: User-friendly interactive interface for managing configurations and running fuzzing sessions.
- **Common Paths**: Auto-detection of commonly used paths (e.g., `/admin`, `/login`).

---
## Requirements
Python
aiohttp

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/NasHLabx/StreamFuzz.git
   cd StreamFuzz
   pip install -r requirements.txt
   python stream.py 

## License
This project is licensed under the MIT License. See the **LICENSE** file for details

 ## Author
Mr. Goodluck Nasharmy(NasHLabx).
