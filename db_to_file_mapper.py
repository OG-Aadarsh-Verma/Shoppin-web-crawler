from project.database.db import Database

def fetch_products_grouped_by_domain():
    db = Database()
    product_collection = db.get_product_collection()

    domain_to_products = {}

    try:
        products = product_collection.find({}, {"_id": 0, "domain": 1, "url": 1})

        for product in products:
            domain = product["domain"]
            url = product["url"]

            if domain not in domain_to_products:
                domain_to_products[domain] = []

            domain_to_products[domain].append(url)

    except Exception as e:
        print(f"Error fetching products from the database: {e}")

    finally:
        db.close()

    return domain_to_products

def write_products_to_file():
    grouped_products = fetch_products_grouped_by_domain()

    try:
        with open('./product_urls.txt', 'w') as file:
            for domain, urls in grouped_products.items():
                file.write(f"{domain}:\n")
                for url in urls:
                    file.write(f"\t- {url}\n")
                file.write("\n")
        print("Product URLs successfully written to 'product_urls.txt'.")
    except Exception as e:
        print(f"Error writing products to file: {e}")

if __name__ == "__main__":
    write_products_to_file()
