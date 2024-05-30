import requests
import scrape_urls

def download_datasets(urls, destination_folder):
    failed_urls = []
    failed_count = 0
    good_urls = []
    good_count = 0
    for i, url in enumerate(urls):
        response = requests.get(url)
        if response.status_code == 200:
            # Create a file path based on the URL
            filename = url.split("/")[-1]
            destination_path = f"{destination_folder}/{filename}"
            with open(destination_path, 'wb') as file:
                file.write(response.content)
            print(f"Dataset {i+1} downloaded successfully.\n")
            good_urls.append(url)
            good_count += 1
        else:
            print(f"Failed to download dataset {i+1}. URL: {url}\n")
            failed_count += 1
            failed_urls.append(url)
    print("====DOWNLOAD RESULTS====")
    print(failed_count)
    print(",".join(failed_urls))
    print(good_count)
    print(",".join(good_urls))
# Example usage:
download_urls = []
url = "https://www.datos.gob.mx/busca/dataset/programa-de-fertilizantes-2023-listados-autorizados"
urls = scrape_urls.scrape_urls(url)
for url in urls:
    download_urls.append(url)

download_destination_folder = "data/productores_autorizados"
download_datasets(download_urls, download_destination_folder)