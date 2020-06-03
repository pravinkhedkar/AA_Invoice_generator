import bs4
import requests
import pandas as pd
import time
start = time.time()
main_dic={"store_name":[],"Rating":[],"Mobile No":[],"store_address":[]}
# url = "https://www.justdial.com/Pune/Milk-Dairy/page-"
headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0','Host':'www.justdial.com'}
for z in range(1,50):
    url = "https://www.justdial.com/Pune/Milk-Dairy/page-"
    url +="{}".format(z)
    content = requests.get(url,headers=headers)
    soup = bs4.BeautifulSoup(content.content, 'html5lib')
    print("Iteration {} started : url: {}".format(z,url))
    # fd =open('/home/pravin/Desktop/output.html')
    # soup = bs4.BeautifulSoup(fd.read(), 'html5lib')
    dic= {"fe":"(","ba":'-',"hg":")","dc":"+","ji":"9","yz":"1","rq":"5","wx":"2","vu":"3","po":"6","nm":"7","ts":"4","lk":"8","acb":"0"}
    def get_mob_no(s):
        mob_no = "".join([dic[ic] for ic in s])
        return mob_no if mob_no is not None else "N/A"
    table = soup.find('ul', attrs = {'class':'rsl col-md-12 padding0'})
    for row in table.find_all_next(attrs = {'class': 'col-sm-5 col-xs-8 store-details sp-detail paddingR0'}):
        store=""
        for r in row.children:
            is_contact = False
            is_name=False
            is_rating=False
            is_address= False
            store_name="N/A"
            store_rating="N/A"
            mob_no="N/A"
            store_address="N/A"
            for i in r.find_next_siblings(attrs = {'class':['store-name','newrtings','contact-info','address-info tme_adrssec']}):
                if i['class'][0] ==  'store-name': #i['class'] => list of classes
                    store_name = i.find('span',attrs = {'class' : 'lng_cont_name'}).string.strip("/n")
                    main_dic['store_name'].append(store_name)
                    is_name=True
                if i['class'][0] == 'newrtings':
                    store_rating = i.find('span',attrs = {'class' : "green-box"}).string.strip("/n")
                    main_dic['Rating'].append(store_rating)
                    is_rating=True
                if i['class'][0] == 'contact-info':
                    is_contact=True
                    no_list=[]
                    try:
                        for j in i.find('b').children:
                            no_list.append(j['class'][1].split('-')[1])
                    except Exception as identifier:
                        for j in i.find('a').children:
                            no_list.append(j['class'][1].split('-')[1])
                    mob_no= get_mob_no(no_list)
                    main_dic['Mobile No'].append(mob_no)
                if i['class'][0] ==  'address-info': 
                    store_address = i.find('span',attrs = {'class' : 'cont_fl_addr'}).string.strip("/n")
                    is_address=True
                    main_dic['store_address'].append(store_address)
                    # print(store_address)
            if not is_contact:
                main_dic['Mobile No'].append(mob_no)
            if not is_rating:
                main_dic['Rating'].append(store_rating)
            if not is_name:
                main_dic['store_name'].append(store_name)
            if not is_address:
                main_dic['store_address'].append(store_address)
            break

    # if z==1:
    #     print(main_dic)
df=pd.DataFrame(main_dic)
df.to_csv("/home/pravin/Desktop/Dairy.csv")
end_time = time.time()

print("Completed.. time required {}".format(end_time-start))
  
        