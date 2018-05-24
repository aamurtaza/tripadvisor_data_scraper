# importing libraries
from bs4 import BeautifulSoup
import urllib
import os
import urllib.request

base_path =  os.path.dirname(os.path.abspath('__file__'))   


file = open(os.path.expanduser(r""+base_path+"/datasets/Hotels_Reviews.csv"), "wb")
file.write(b"name,current_price_per_night,average_rating,total_reviews_received,address,lat,lng,reviewer_nationality,rating,review_title,review"+ b"\n")
      
trip_advisor_url = "https://www.tripadvisor.com"
WebSites = [
    trip_advisor_url+"/Hotels-g189896-Finland-Hotels.html"]

# looping through each site until it hits a break
for page_url in WebSites:
    page_source = urllib.request.urlopen(page_url).read()
    soup = BeautifulSoup(page_source, "lxml")
    divs = soup.find_all('div', { "class" : "hotel_content easyClear sem" })
    
    for hotel_content in divs:
        
        # Extract name, url
        listing_title = hotel_content.find('div', { "class" : "listing_title" })
        name = listing_title.find('a').contents[0]
        name = name.replace(",", "")
        print(name)
        url = listing_title.find('a')['href']
        url = trip_advisor_url + url               
                
         #Extract current_price_per_night
        price_div = hotel_content.find('div', { "class" : "price" })
        price_span = price_div.select_one("span")
        current_price_per_night = price_span.text
   
        # Extract average_rating
        average_rating_div = hotel_content.find('div', { "class" : "bubbleRating" })
        average_rating = average_rating_div.select_one("span")["content"]
        
        # Extract total_reviews_received, reviews_url 
        reviews_span = hotel_content.find('span', { "class" : "reviewCount" })
        if (reviews_span == None):
            total_reviews_received = "0"
            continue
        else:
            total_reviews_received = reviews_span.text.split(' ')[0].replace(",","")
            print(total_reviews_received)
            reviews_url = reviews_span.find('a')['href']
            reviews_url = trip_advisor_url + reviews_url
        
        hotel_page_source = urllib.request.urlopen(reviews_url).read()
        hotel_soup = BeautifulSoup(hotel_page_source, "lxml")
        page = 1 
        while True:      
                      
            # Extract Lat, Lng
            lat = lng = ""
            all_script  = hotel_soup.find_all("script", {"src":False})
            keys = ['lat', 'lng']
            for script in all_script:
                all_value =  script.string   
                if (all_value == None):
                    continue
                for line in all_value.splitlines():
                    if line.split(':')[0].strip() in keys:
                        if (line.split(':')[0].strip() == keys[0]):
                            lat = line.split(':')[1].strip()
                        else:
                            lng = line.split(':')[1].strip()
            lat = lat.replace(",", "")
            lng = lng.replace(",", "")
                
            # Extract Address
            address_div = hotel_soup.find('div', { "class" : "prw_rup prw_common_atf_header_bl headerBL"})
            street_address = address_div.find('span', { "class" : "street-address" }).text
            locality = address_div.find('span', { "class" : "locality" }).text
            if (len(locality.split(' ')) > 2):
                city = locality.split(' ')[0]
                postal_code = locality.split(' ')[1]
            else:
                city = ""
                postal_code = ""
            country = address_div.find('span', { "class" : "country-name" }).text
            address = street_address + " " + locality + " " + country
            address = address.replace(",", "")
            
            reviews = hotel_soup.find_all('div', {"class": "review-container"})
            
            # Loop through all reviews aavailable on page
            for review in reviews:
                # Extract reviewer_name
                reviewer_name_div = review.find('div', {"class": "username mo"})
                if (reviewer_name_div == None):
                    reviewer_name = ""
                else:
                    reviewer_name = reviewer_name_div.find("span", {"class": "expand_inline scrname"}).text
                    reviewer_name = reviewer_name.replace(",", " ")
                    
                # Extract reviewer_nationality
                reviewer_location_div = review.find('div', {"class": "location"})
                if (reviewer_location_div == None):
                    reviewer_nationality = ""
                else:
                    reviewer_nationality = reviewer_location_div.find("span", {"class": "expand_inline userLocation"}).text
                    reviewer_nationality = reviewer_nationality.replace(",", " ")
                    
                    
                # Extract rating_given_by_reviewer, review_date
                rating_div = review.find("div", {"class": "rating reviewItemInline"})
                if (rating_div == None):
                    rating = ""
                else: 
                    if (rating_div.find("span", {"class": "ui_bubble_rating bubble_50"}) != None):
                        rating = 5
                    elif (rating_div.find("span", {"class": "ui_bubble_rating bubble_40"}) != None):
                        rating = 4
                    elif (rating_div.find("span", {"class": "ui_bubble_rating bubble_30"}) != None):
                        rating = 3
                    elif (rating_div.find("span", {"class": "ui_bubble_rating bubble_20"}) != None):
                        rating = 2
                    elif (rating_div.find("span", {"class": "ui_bubble_rating bubble_10"}) != None):
                        rating = 1
                    else:
                        rating = ""
                   
                    review_date_span = rating_div.find("span", {"class": "ratingDate relativeDate"})
                    if (review_date_span != None):
                        review_date = review_date_span["title"] 
                    else:
                        review_date = ""
                    
                # TODO Add day_since_fetch column after finlaizing dataset    
                # Extract review_title, 
                review_title_div = review.find("div", {"class": "quote"})
                if (review_title_div != None):
                    review_title_span = review_title_div.find("span", {"class": "noQuotes"})
                    if (review_title_span != None):
                        review_title = review_title_span.text
                    else:
                        review_title = ""
                else:
                    review_title = ""
                review_title = review_title.replace(",", " ")
                
              
                # TODO Add review_words_count column after finlaizing dataset
                # Extract review
                review_div = review.find("div", {"class": "prw_rup prw_reviews_text_summary_hsx"})
                if (review_div == None):
                    review = ""
                else:
                    partial_review = review_div.find("p", {"class": "partial_entry"})
                    if (partial_review == None):
                        review = ""
                    else:
                        review = partial_review.text[:-6]
                review = review.replace(",", " ")
                review = review.replace("\n", " ")
                
                
                # Add Record
                record = str(name) + "," + str(current_price_per_night) + "," + str(average_rating) + "," + str(total_reviews_received) + "," + str(address) + "," + str(lat) + "," + str(lng) + "," + str(reviewer_nationality) + "," + str(rating) + "," +str(review_title) + "," + str(review)                    
                
                file.write(bytes(record, encoding="ascii", errors='ignore')  + b"\n")
            
            # Extract pagination url 
            count = float(total_reviews_received)/10
            if (count > 150):
                count = 150
            pagination_div = hotel_soup.find('div', { "class" : "unified pagination north_star "})
            page_div = hotel_soup.find('div', { "class" : "pageNumbers"})
            pagination_spans = page_div.find_all('span', { "class" : "pageNum taLnk " })
            next_url = ""
            if ((page < count) & (len(pagination_spans) > 3)):
                page = page + 2
                next_url = pagination_spans[3]['data-href'] 
                next_url = trip_advisor_url + next_url
                hotel_page_source = urllib.request.urlopen(next_url).read()
                hotel_soup = BeautifulSoup(hotel_page_source, "lxml")
            else:
                break        
file.close() 
        
   