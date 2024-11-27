# Hosts: https://github.com/StevenBlack/hosts
# These links contains bloated links for the following categories
# Alternate: https://github.com/hagezi/dns-blocklists
# Alternate: https://firebog.net

URLS = {
    "ADWARE_MALWARE_LINK": {
        "url": 'https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts',
        "enabled": True #change this to False if you don't need protection from this category
    },
    "FAKE_NEWS": {
        "url": 'https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/fakenews-only/hosts',
        "enabled": True #change this to False if you don't need protection from this category
    },
    "GAMBLING": {
        "url": 'https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/gambling-only/hosts',
        "enabled": True #change this to False if you don't need protection from this category
    },
    "PORN": {
        "url": 'https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/porn-only/hosts',
        "enabled": True #change this to False if you don't need protection from this category
    },
    "SOCIAL": {
        "url": 'https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/social-only/hosts',
        "enabled": True #change this to False if you don't need protection from this category
    },
}

# DNS Settings
DNS_PORT = 53
CLOUDFLARE_DNS = "1.1.1.1"
GOOGLE_DNS = "8.8.8.8"
