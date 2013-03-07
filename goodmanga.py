#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, urllib, re, csv, time
from Tkinter import *
import tkMessageBox
import urllib

type_list = 'jpg|jpeg|png|gif|bmp'

def table_writer(filename,header):
    wr = csv.DictWriter(file(filename, "w"),fieldnames=header)
    wr.writerow(dict(zip(header,header)))
    return wr

    ''' EXAMPLE
    #csvfile = table_writer('manga-naruto-directory.csv', ['chapter','link']) #create
    #csvfile.writerow({'chapter': 'value', 'link': 'value'}) #insert
    #for line in csv.DictReader(open(filename)): #read
    '''

def get_chapter_no(name):
    chapter = str(name.split('/')[-1])
    chapter = ''.join(x for x in chapter if x.isdigit())
    return chapter

def get_chapter_list(filename):
    chapters = ()
    for line in csv.DictReader(open(filename)):
        chapters += (line["chapter"],)
    return chapters

def filter_links(links):
    links_tmp = []
    for link in links:
        link = link.split('"')[0]
        if 'page' not in link:
            links_tmp.append(link)
    return links_tmp

def get_latest_chapter(url, keyword):
    latest_chapter = False
    target_page = urllib.urlopen(url)
    main_page = target_page.read()
    target_page.close()
    chapter_links = re.findall(r"(http://www.goodmanga.net\S+%s\S+\")" %(keyword) ,main_page)
    chapters = []
    for line in chapter_links:
        chapter = get_chapter_no(line)
        chapters.append(int(chapter))
    latest_chapter = max(chapters)
    return latest_chapter

def get_next_page(src):
    next_page = False
    next_page = True if re.findall(r"(Next)" ,src) else False

    return next_page

def get_chapter_page(src):
    num_pages = re.findall(r"(of.*span>)", src)
    if len(num_pages) == 2:
        if num_pages[0] == num_pages[1]:
            num_pages = num_pages[0]
    num_pages = int(''.join(x for x in num_pages if x.isdigit()))

    return num_pages

def prepare_url(url, keyword):
    print "Find relate page url..."
    latest_chapter = int(get_latest_chapter(url, keyword))
    ratio = (float(latest_chapter) / float(50)) - (float(latest_chapter) % float(50))
    num_pages = (float(latest_chapter) % float(50)) if ratio == 0.0 else (float(latest_chapter) % float(50)) + 1

    links = []
    for p in range(1,int(num_pages)+1):
        link = url+'?page=%s'%p
        links.append(link)

    links.sort()
    links[0] = links[0].split('?')[0]
    urls = links

    print "Page Found >>>",len(urls)
    return urls

def generate_record(urls, keyword):
    ''' scan html to generate record and make csv file '''
    print "Generate Record..."
    records = []
    for url in urls:
        print "Reading...",url
        target_page = urllib.urlopen(url)
        main_page = target_page.read()
        target_page.close()
        #create source file
        links = re.findall(r"(http://www.goodmanga.net\S+%s\S+\")" %(keyword) ,main_page)
        chapter_links = filter_links(links)
        for line in chapter_links:
            chapter = get_chapter_no(line)
            record = { 'chapter': int(chapter), 'link': line}
            if record not in records:
                records.append(record)

    print "Generate Record >>>", len(records)
    return records

def generate_csv(keyword, records):
    filename = 'manga-%s-directory.csv'%(keyword)
    csvfile = table_writer(filename, ['chapter','link'])
    csvfile.writerows(records)
    #chapters = get_chapter_list(filename)
    #for record in records:
        #print record
        #csvfile.writerow({'chapter': record["chapter"], 'link': record["link"]})
    print "Generate CSV >>> OK"
    return True

def download_link(url, keyword, records):
    #start download link from source file 
    print "Start Downloading..."
    if url:
        records = []
        fp = urllib.urlopen(url)
        records.append({'chapter':'', 'link':''})

    if records:
        for record in records:
            fp = urllib.urlopen(record["link"])

            # chapter pages (integer)
            main_page = fp.read()
            num_pages = get_chapter_page(main_page)
            images = []
            for p in range(1,num_pages+1):
                sub_page = urllib.urlopen(record["link"]+'/%s'%p)
                sub_page = sub_page.read()
                search_txt = '%s/%s/%s'%(keyword, str(record['chapter']), p)
                #find image url by using regexpr
                image = re.findall(r"(http\S+%s\.(?:%s))" %(search_txt, type_list), sub_page)
                images.append(image[0])

            chapter = str(record['chapter'])
            directory = r'source/%s/manga-%s-'%(keyword, keyword) + chapter
            if not os.path.exists(directory): os.makedirs(directory)
            count = 1
            print "-" * 100
            print "%s Chapter : %s" %(keyword, chapter)
            for image in images:
                pic_type = "." + image.split('.')[-1]
                pic_name = 'manga-%s-'%(keyword) + chapter + '-' + str(count).zfill(3) + pic_type
                save_path = directory + '/' + pic_name

                if os.path.exists(save_path):
                    method = 'skip'
                else:
                    method = 'download'

                if method == 'download':
                    urllib.urlretrieve(image, save_path)

                print "%s %s (%s/%s) : " % (method, chapter, count, len(images)), save_path
                count += 1


    fp.close()
    return True 

def fetch_manga():
    url = txt_url.get()
    #url = 'http://www.goodmanga.net/50/air_gear'
    if not url:
        print "Please input url"
        tkMessageBox.showinfo( "Warning", "Please input url")
        txt_url.icursor(txt_url.index())

    keyword = url.split('/')[-1].split('?')[0]
    print "Begin Fetch...",keyword

    urls = prepare_url(url, keyword)

    records = generate_record(urls, keyword)

    gen_csv = generate_csv(keyword, records)

    dl_status = download_link('',keyword, records)

    print "-- FINISHED --"
    return True 

#declare parent form
tk = Tk()

#add label to parent form
label = Label(tk, text="Goodmanga URL ", justify=LEFT)
label.pack(side=LEFT)

#add textbox to parent form
txt_url = Entry(tk, bd=3,width=50)
txt_url.pack(side=LEFT)

#add button to parent form
btn_download = Button(tk, text="download", command=fetch_manga)
btn_download.pack(side=RIGHT)

#start gui
tk.mainloop()

