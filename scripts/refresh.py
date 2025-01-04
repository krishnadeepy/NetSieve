import requests
from sqlalchemy.orm import Session
from config import URLS
from models import HostEntry, SessionLocal  

def parse_hosts_content(content, category):
    hosts = []
    for line in content.splitlines():
        line = line.strip()
        if line.startswith('#') or not line:
            continue  

        parts = line.split()
        if len(parts) >= 2:
            ip = parts[0]
            hostnames = parts[1:]
            for hostname in hostnames:
                if hostname.startswith('#'):
                    break  
                hosts.append(HostEntry(ip=ip, hostname=hostname, category=category))

    return hosts

def fetch_and_parse(category, url):
    """
    Fetches and parses the hosts file for a given category.
    """
    try:
        # Fetch the data using requests
        response = requests.get(url)
        response.raise_for_status()
        content = response.text

        # Parse the content into host entries
        hosts = parse_hosts_content(content, category)

        # Save to the database (using bulk insert for better performance)
        with SessionLocal() as db:
            # Check if the data already exists to avoid duplicates
            existing_entries = db.query(HostEntry).filter(
                HostEntry.category == category
            ).all()
            
            # Collect host entries to be added to avoid duplicates
            existing_entries_set = {(entry.ip, entry.hostname) for entry in existing_entries}
            new_entries = [host for host in hosts if (host.ip, host.hostname) not in existing_entries_set]

            # Use bulk save for new entries
            if new_entries:
                db.bulk_save_objects(new_entries)
                db.commit()

        return category, len(new_entries), None  # No error
    except Exception as e:
        return category, 0, str(e)  # Return error message if any



def main():
    # Filter enabled URLs
    enabled_urls = {cat: data["url"] for cat, data in URLS.items() if data["enabled"]}
    # Iterate through the URLs
    for category, url in enabled_urls.items():
        category, count, error = fetch_and_parse(category, url)
        if error:
            print(f"Error processing {category}: {error}")
        else:
            print(f"Processed category {category}: {count} host entries")


if __name__ == "__main__":
    main()
