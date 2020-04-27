from bs4 import BeautifulSoup
import json
import webbrowser
import requests
import sqlite3
import csv


class brand:
    def __init__(self, name, url, products):
        self.name=name
        self.url=url
        self.products= products


class product:

    def __init__(self, name, url, brand_name,price=None, number=None ,category=None, in_stock=None, ingredients=None, details=None, size=None , use=None , cruelty_free=None):
        self.name=name 
        self.url=url 
        self.brand_name=brand_name 
        self.price=price 
        self.category=category 
        self.in_stock=in_stock 
        self.ingredients=ingredients 
        self.details=details 
        self.size=size 
        self.use=use 
        self.number=number 
        self.cruelty_free=cruelty_free 

    def print_info(self):
        print(self.name+'\n')
        try:
            price_split=self.price.split(' ')
            price=price_split[1]
            print('onsale!')
            print(price)
            old_price=price_split[0]
            print(f'orginal price: {old_price}')
        except:
            print(f'Price: {self.price}')
        print(f'Category: {self.category}')
        print(f'Size: {self.size}')
        print(f'Cruelty Free: {self.cruelty_free}')
        print(f'In stock: {self.in_stock}\n')
        print(f'Details:\n{self.details}\n')
        print(f'Use:\n{self.use}\n')
        print(f'Ingredients: \n{self.ingredients}\n')



def load_cache():
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache

def save_cache(cache): 
    cache_file = open(CACHE_FILENAME, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()


def get_brand_instance(url, cache_dict):
    if url in cache_dict.keys():
        product_response_text=cache_dict[url]
        print('using cache')
    else:
        response=requests.get(url)
        product_response_text=response.text
        cache_dict[url]=product_response_text
        save_cache(cache_dict)

    soup_two = BeautifulSoup(product_response_text, 'html.parser')
    name=soup_two.find('h3', class_='css-xwgz3s').text
    products=soup_two.find_all('span', class_='css-pelz90')
    product_list=[]
    for item in products:
        if '(' in item.text:
            pass
        else:
            product_list.append(item.text)

    product_link=soup_two.find_all('a', class_='css-ix8km1')
    product_link_list=[]
    for item in product_link:
        product_link_list.append(item['href'])
    product_dict=dict(zip(product_list, product_link_list))
    brand_var=brand(name=name, url=url, products=product_dict)
    return brand_var


def get_product_instance(url, brand, list, cache_dict):
    if url in cache_dict.keys():
        print('Caching!!!!'*10)
        item_response_text=cache_dict[url]
    else:
        print('LOADING LOADING LOADING'*10)
        response=requests.get(url)
        item_response_text=response.text
        cache_dict[url]=item_response_text
        save_cache(cache_dict)   
    soup_three = BeautifulSoup(item_response_text, 'html.parser')
   #assign size and Item No
    try:
        size=soup_three.find('div', class_='css-6dchx0' ).text
        item_no=None
    except:
        try:
            size_and_item=soup_three.find('div', class_='css-v7k1z0' ).text.split('•')
            size=size_and_item[0].split('SIZE ')[1]
            item_no=size_and_item[1].split('ITEM ')[1]
        except:
            size=None
            item_no=None
    info=soup_three.find_all('div', class_='css-pz80c5')
    details=info[0].text
    try:
        use=info[1].text
    except: 
        use=None
    try:
        try:
            ingredients=info[2].text.split('Clean at Sephora products are formulated without')[0]
        except:
            ingredients=info[2].text
    except:
        ingredients=None
    if ingredients==None:
        try:
            ingredients=info[1].text
            use=None
        except:
            pass        
    if brand in list:
        cruelty_free='Yes'
    else:
        cruelty_free='No'
    product_instance=product(name = soup_three.find('span', class_='css-0' ).text , brand_name=brand , number=item_no, url=url,  price=soup_three.find('div', class_='css-slwsq8' ).text, category=soup_three.find('a',class_="css-dvzm2b").text, in_stock=soup_three.find('span', class_='css-7es9ld '), ingredients=ingredients, details=details, size=size, use=use, cruelty_free=cruelty_free)
    return product_instance


def build_cruelty_free_list(cache_dict):
    url='https://www.crueltyfreekitty.com/cruelty-free-sephora-brands/'
    if url in cache_dict.keys():
        response_text=cache_dict[url]
    else:
        response = requests.get(url)
        response_text=response.text
        cache_dict[url]=response_text
        save_cache(cache_dict)
    soup = BeautifulSoup(response_text, 'html.parser')
    district=soup.find_all('ul', class_="sephora-list heart")
    test=district[3].find_all('a')
    test_list=[]
    for items in district:
        test=items.find_all('a')
        for brand in test:
            test_list.append(brand.text.lower())
    return test_list

def create_csv_list():
    filename='sephora-reviews.csv'
    data=[]
    with open(filename, 'r', encoding='utf-8-sig') as file_obj: 
        reader = csv.DictReader(file_obj, fieldnames=['Item Number','Name','Brand','Description','Url','Rating','ReviewText'])
        row = 0
        for dictionary in map(dict, reader):
            if row > 0: data.append(dictionary)
            row += 1
    return data

def create_db():
    conn = sqlite3.connect('sephora.sqlite')
    cur = conn.cursor()

    drop_brands_sql = 'DROP TABLE IF EXISTS "Brands"'
    drop_products_sql = 'DROP TABLE IF EXISTS "Products"'
    
    create_brands_sql = '''
        CREATE TABLE IF NOT EXISTS "Brands" (
            "Id" INTEGER PRIMARY KEY AUTOINCREMENT, 
            "Name" TEXT NOT NULL,
            "Url" TEXT NOT NULL, 
            "ProductCount" TEXT NOT NULL
        )
    '''
    create_products_sql = '''
        CREATE TABLE IF NOT EXISTS 'Products'(
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            "Name" TEXT NOT NULL,
            'BrandName' TEXT NOT NULL,
            'Category' TEXT NOT NULL,
            'Price' TEXT NOT NULL,
            'Size' TEXT,
            'ItemNumber' TEXT,
            'CrueltyFree' TEXT NOT NULL,
            'URL' TEXT NOT NULL,
            'Ingredients' TEXT,
            'Details' TEXT,
            'Use' TEXT )
    '''
    cur.execute(drop_brands_sql)
    cur.execute(drop_products_sql)
    cur.execute(create_brands_sql)
    cur.execute(create_products_sql)
    conn.commit()
    conn.close()

def load_brands(object_list): 

    insert_brand_sql = '''
        INSERT INTO Brands
        VALUES (NULL, ?, ?, ?)
    '''

    conn = sqlite3.connect('sephora.sqlite')
    cur = conn.cursor()
    for c in object_list:
        cur.execute(insert_brand_sql,
            [
                c.name,
                c.url,
                len(c.products),
            ]
        )
    conn.commit()
    conn.close()


def load_products(object_list): 

    insert_product_sql = '''
        INSERT INTO Products
        VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)
    '''

    conn = sqlite3.connect('sephora.sqlite')
    cur = conn.cursor()
    for c in object_list:
        cur.execute(insert_product_sql,
            [
                c.name,
                c.brand_name,
                c.category,
                c.price,
                c.size,
                c.number,
                c.cruelty_free,
                c.url,
                c.ingredients,
                c.details,
                c.use,

            ]
        )
    conn.commit()
    conn.close()





if __name__ == "__main__":
    alpha_dict={'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8, 'j': 9, 'k': 10, 'l': 11, 'm': 12, 'n': 13, 'o': 14, 'p': 15, 'q': 16, 'r': 17, 's': 18, 't': 19, 'u': 20, 'v': 21, 'w': 22, 'y': 23}
    divider='---------------------------------'
    end=''
    product_end=''
    CACHE_FILENAME='sephora.json'
    cache_dict=load_cache()
    cruelty_free_list=build_cruelty_free_list(cache_dict)
    brand_object_list=[]
    product_object_list=[]
    create_db()
    review_list=create_csv_list()


    #user selects experience 
    print(divider)
    while True:
        url = 'https://www.sephora.com/'
        brand_list_url=url+'brands-list'
        if brand_list_url in cache_dict.keys():
            response_text=cache_dict[brand_list_url]
        else:    
            response = requests.get(brand_list_url)
            response_text=response.text
            cache_dict[brand_list_url]=response_text
            save_cache(cache_dict)
        #searching brands by first name
        soup = BeautifulSoup(response_text, 'html.parser')
        district=soup.find_all('ul', class_="css-isj0xt")
        while True:
            print('Search Brands From Sephora!')
            print('Menu:\n 1.Explore Brands By First Letter\n 2.Search a Brand\n 3.Quit\n')
            print(divider)
            inital_input=input('Select: ')
            if inital_input=='1' or inital_input.lower()=='explore brands by first letter':
                while True:
                    brand_dict={}
                    x=input('Explore a Brand by First Letter: ').lower()
                    if x.lower()=='quit':
                        print('Buh-Bye!')
                        quit()
                    try:
                        if len(x) >1 or x.isnumeric():
                            print('Invalid Output')
                            pass
                        else:
                            print(divider)
                            test=district[alpha_dict[x]].find_all('a', class_="css-ekc7zl")
                            for a in test:
                                brand_dict[a.get_text().lower().replace('\xa0','')]=a['href']
                            for keys in brand_dict.keys():
                                print(keys)
                            print(divider)  
                            crawl=input('select a brand to see top products:')
                            print(divider)
                            break
                    except:
                        print(f'Sorry, No Brands Begin with the Letter "{x}"')       
                break        
                #searching brands directly    
            elif inital_input=='2' or inital_input.lower()=='search a brand':
                while True:
                    brand_dict={}
                    crawl=input('Search brand name: ')
                    if crawl.lower()=='quit':
                        print('Buh-Bye!')
                        quit()
                    print(divider)
                    x=crawl[0].lower()
                    test=district[alpha_dict[x]].find_all('a', class_="css-ekc7zl")
                    for a in test:
                        brand_dict[a.get_text().lower().replace('\xa0','')]=a['href'][0:]
                    if crawl not in brand_dict.keys():
                        print(f'Sorry, {crawl} is not carried at Sephora.')
                        pass
                    else:
                        break
                break        
            elif inital_input=='3' or inital_input.lower()=='quit':
                try:
                    load_brands(brand_object_list)
                except:
                    pass
                try:
                    load_products(product_object_list)
                except:
                    pass
                print('Buh-Bye')
                quit()                     
            else:
                print('invalid input!')
                pass
        #crawl to brand product page
        brand_object=get_brand_instance('https://www.sephora.com'+ brand_dict[crawl], cache_dict)
        brand_object_list.append(brand_object)

        product_dict=brand_object.products
        product_list=[]
        while True:
            i=1    
            for key in product_dict.keys():
                print(f'{i}. {key}')
                product_list.append(key)
                i=i+1
            print(divider)
            # print('select a number to learn more\n')
            product_input=int(input('Type number: '))-1
            print(divider)
            product_url=url+ product_dict[product_list[product_input]]
            test_instance=get_product_instance(product_url, brand_object.name, cruelty_free_list, cache_dict)
            product_object_list.append(test_instance)
            print(test_instance.brand_name)
            print(test_instance.name)
            test_instance.print_info()

            print(divider)
            print('Menu: \n 1. Read Product Review\n 2. View product on Sephora.com \n 3. Back to Product List \n 4. Back to Main Menu \n 5. Quit \n')
            menu_input=input('Select: ')
            if menu_input=='1':
                print(divider)
                print(f'\nProduct Review for {test_instance.name}\n')
                count=0
                for row in review_list:
                    if row['Brand']==test_instance.brand_name and row['Name']==test_instance.name:
                        print(f'Rating:{row["Rating"]}')
                        print(f'{row["ReviewText"]}\n')
                        count=count+1
                        if count==10:
                            break
                if count==0:
                    print('Sorry, this product does not have reviews\n')    
                    print(divider)    
                break        
            if menu_input=='2':
                print('You are being redirected to Sephora.com!')
                webbrowser.open_new(product_url)
                break
            if menu_input=='5' or menu_input.lower()=='quit':
                load_brands(brand_object_list)
                load_products(product_object_list)
                print('Buh-Bye')
                quit()
            if menu_input=='3':
                pass
            if menu_input=='5':
                break           

           