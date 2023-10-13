import os
import dotenv

dotenv.load_dotenv()

BOT_NAME = "autoria-parser"

SPIDER_MODULES = ["src.spiders"]
NEWSPIDER_MODULE = "src.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = "src (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = int(os.getenv("CONCURRENT_REQUESTS", "16"))

# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = int(os.getenv("CONCURRENT_REQUESTS_PER_DOMAIN", "8"))

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
# }

# Enable or disable spider middlewares
# SPIDER_MIDDLEWARES = {
#    "src.middlewares.SrcSpiderMiddleware": 543,
# }

# Enable or disable downloader middlewares
# DOWNLOADER_MIDDLEWARES = {
#    "src.middlewares.SrcDownloaderMiddleware": 543,
# }

# Enable or disable extensions
# EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
# }

# Configure item pipelines
# ITEM_PIPELINES = {
#    "src.pipelines.SrcPipeline": 300,
# }

# Enable and configure the AutoThrottle extension (disabled by default)
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = "httpcache"
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

DB_DRIVER = "postgresql"
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "")
DB_DATABASE = os.getenv("DB_DATABASE", "db_name")

DB_URL = f"{DB_DRIVER}://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
