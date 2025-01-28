from apify_client import ApifyClient
import json

# Initialize the ApifyClient with your Apify API token
# Replace '<YOUR_API_TOKEN>' with your token.
client = ApifyClient("apify_api_BAHIGIseqs4pjaDXd6lbFfqhF9izJg47kNT2")

# Prepare the Actor input
run_input = {
    "query": "Montreal",
    "maxItemsPerQuery": 1300,
    "language": "en",
    "currency": "USD",
    "locationFullName": "Montreal",
}

# Run the Actor and wait for it to finish
run = client.actor("maxcopell/tripadvisor").call(run_input=run_input)

print("Run ID:", run["defaultDatasetId"]) 

items = []
count = 0
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    items.append(item)
    count += 1
    if count <= 3:  # Print first 3 items to check structure
        print(f"\nItem {count}:")
        print(json.dumps(item, indent=2))
    if count == 1:  # Print available keys for first item
        print("\nAvailable data fields:", list(item.keys()))

print(f"\nTotal items collected: {count}")


# Save to JSON file
with open('tripadvisor_data.json', 'w', encoding='utf-8') as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

# # To read the data later:
# with open('tripadvisor_data.json', 'r', encoding='utf-8') as f:
#     loaded_data = json.load(f)

# # Example: Print each item's name (adjust based on your actual data structure)
# for item in loaded_data:
#     print(item.get('name', 'No name available'))

print("\nData saved to tripadvisor_data.json")

# # Fetch and print Actor results from the run's dataset (if there are any)
# print("💾 Check your data here: https://console.apify.com/storage/datasets/" + run["defaultDatasetId"])
# for item in client.dataset(run["defaultDatasetId"]).iterate_items():
#     print(item)
