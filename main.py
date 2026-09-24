from webscrapping.Puma import Puma
from webscrapping.Saucony import Saucony
from webscrapping.RunLab import RunLab
from webscrapping.NewBalance import NewBalance
from webscrapping.Adidas import Adidas
from webscrapping.ArenaStore import ArenaStore
from webscrapping.Epicentr import Epicentr
import pandas as pd
import csv

def main():
    puma_obj = Puma()
    puma_list = puma_obj.view_resource()
    print('Puma list------------------------')
    print(puma_list)
    #saucony_obj = Saucony()
    #saucony_list = saucony_obj.view_resource()
    #print('Saucony list------------------------')
    #print(saucony_list)
    #runlab_obj = RunLab()
    #runlab_list = runlab_obj.view_resource()
    #print('RunLab list------------------------')
    #print(runlab_list)
    #newbalance_obj = NewBalance()
    #newbalance_list = newbalance_obj.view_resource()
    #print('NewBalance list------------------------')
    #print(newbalance_list)
    #adidas_list = []
    #adidas_obj = Adidas()
    #adidas_obj.view_resource(adidas_list)
    #print('Adidas list------------------------')
    #print(adidas_list)
    #arenastore_obj = ArenaStore()
    #arenastore_list = arenastore_obj.view_resource()
    #print('ArenaStore list------------------------')
    #print(arenastore_list)
    #epicentr_obj = Epicentr()
    #epicentr_list = epicentr_obj.view_resource()
    #print('ArenaStore titles------------------------')
    #print(epicentr_list)
    #df_ = pd.DataFrame(epicentr_list)
    #print(df_['Title'])
    with open('puma.csv', 'w', newline='', encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=['Model',
                    'Sku', 'Raw_Price', 'Raw_Old_Price'])
        writer.writeheader()
        writer.writerows(puma_list)
    #processed_items = []
    #with open('epicentr_data.csv', mode='r', encoding='utf-8-sig') as infile:
    #    reader = csv.DictReader(infile)
    #    for row in reader:
    #        title = row.get('Title', '') or row.get('title', '')
    #        new_sku = extract_sku(title)
    #        processed_items.append({
    #            'Title': title,
    #            'Sku': new_sku
    #        })
    #with open('proc_epicentr_data.csv', mode='w', newline='', encoding='utf-8-sig') as outfile:
    #    writer = csv.DictWriter(outfile, fieldnames=['Title', 'Sku'])
    #    writer.writeheader()
    #    writer.writerows(processed_items)

if __name__ == "__main__":
    main()