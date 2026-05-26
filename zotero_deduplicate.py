import requests
import os

ZOTERO_USER_ID = os.getenv('ZOTERO_USER_ID')
ZOTERO_API_KEY = os.getenv('ZOTERO_API_KEY')
ZOTERO_BASE_URL = f"https://api.zotero.org/users/{ZOTERO_USER_ID}"

def get_all_items():
    """Fetch all items from Zotero library"""
    items = []
    start = 0
    limit = 100
    
    while True:
        url = f"{ZOTERO_BASE_URL}/items?start={start}&limit={limit}"
        headers = {'Zotero-API-Key': ZOTERO_API_KEY}
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"Error fetching items: {response.status_code}")
            break
        
        batch = response.json()
        if not batch:
            break
        
        items.extend(batch)
        start += limit
    
    return items

def find_duplicates(items):
    """Find duplicate items by title"""
    seen = {}
    duplicates = []
    
    for item in items:
        data = item.get('data', {})
        title = data.get('title', '').lower().strip()
        item_key = item.get('key')
        
        if title:
            if title in seen:
                duplicates.append({
                    'keep': seen[title]['key'],
                    'delete': item_key,
                    'title': data.get('title')
                })
            else:
                seen[title] = {'key': item_key, 'title': data.get('title')}
    
    return duplicates

def delete_item(item_key):
    """Delete an item from Zotero"""
    url = f"{ZOTERO_BASE_URL}/items/{item_key}"
    headers = {'Zotero-API-Key': ZOTERO_API_KEY}
    response = requests.delete(url, headers=headers)
    
    return response.status_code == 204

def main():
    print("Fetching Zotero library...")
    items = get_all_items()
    print(f"Found {len(items)} items")
    
    print("Finding duplicates...")
    duplicates = find_duplicates(items)
    print(f"Found {len(duplicates)} duplicates")
    
    if duplicates:
        print("\nDeleting duplicates...")
        deleted_count = 0
        
        for dup in duplicates:
            if delete_item(dup['delete']):
                print(f"✓ Deleted duplicate: {dup['title']}")
                deleted_count += 1
            else:
                print(f"✗ Failed to delete: {dup['title']}")
        
        print(f"\nDone! Deleted {deleted_count} duplicates")
    else:
        print("No duplicates found!")

if __name__ == "__main__":
    main()
