import requests
import sqlite3
from time import time, sleep, localtime, strftime
from json import loads


def check_delete(delete_status):
    image_delete_status = delete_status == "True"
    """
    check_delete function checks whether the post is deleted or not.
    True - post is deleted 
    False - post is not deleted 
    """ 
    return image_delete_status

def check_rating(rating):
    image_rating = (rating == "g" or rating == "s")
    """
    check_rating function checks whether the post rating is compatible or not.
    True - post has compatible rating
    False - post has incompatible rating 
    """ 
    return image_rating

def check_asr(width, height, tolerance):
    asp_ratio = width/height
    asp_ratio_range  = asp_ratio > 16/9 * (1-tolerance) and asp_ratio < 16/9 * (1+tolerance)
    """
    check_asr function checks whether the image aspect ratio is compatible or not.
    True - image has compatible aspect ratio
    False - image has incompatible aspect ratio
    """
    return asp_ratio_range

def check_area(width, height):
    image_area = width * height
    image_area_range = image_area > 1280*720
    """
    check_area function checks whether the image area is compatible or not.
    True - image has compatible aspect ratio
    False - image has incompatible aspect ratio
    """
    return image_area_range
    
def process_post(post):
    
    post_check = post
    
    img_delete_status = check_delete(post["is_deleted"])
    
    if img_delete_status:
        print("Post is deleted.")
        return False
        
    rating_should_accept = check_rating(post["rating"])
    
    if not rating_should_accept:
        print("Incompatible Rating. Rating:", post["rating"])
        return False

    asr_should_accept = check_asr(
        post["image_width"],
        post["image_height"],
        0.05
    )
    
    if not asr_should_accept:
        print("Incompatible Aspect Ratio.")
        return False
    
    img_area_should_accept = check_area(
        post["image_width"],
        post["image_height"]
    )
    
    if not img_area_should_accept:
        print("Incompatible Image Area.")
        return False
    
    return True


x = 0
sqlite = sqlite3.connect("database.sqlite")
"""-----------------------------------------------------------"""

# make a cursor
cursor_obj = sqlite.cursor()
# execute a query
statement = "SELECT max(id) FROM post"
# read from cursor
cursor_obj.execute(statement)
# extract the maximum ID and set it to x

output = cursor_obj.fetchall()
print("The maximum post id is: ", output[0][0])

sqlite.commit()

if output[0][0] is not None:
    x = output[0][0]

print("x is ", x)
"""-----------------------------------------------------------"""
# split tags 
#post_tags = post["tag_string"]
#print(post_tags.split( ))
# tag url
# search tags 1 x 1 using the tag url
# json file
# get the ID, name, category


tag = None
tag_url = "https://danbooru.donmai.us/tags.json?commit=Search&search%5Bname_or_alias_matches%5D=" + str(tag)


"""-----------------------------------------------------------"""
while True:
    t = localtime()
    current_time = strftime("%T", t)
    print(current_time)
    
    """
    print local time
    """
    # build the URL from a given template
    
    limit = 200
    
    c_url = "https://danbooru.donmai.us/posts.json?page=a" +  str(x) + "&limit=" + str(limit)
 
    # print url (debugging)
    print("Post link: ", c_url)
     
    while True:
        # ask the internet to give us the contents of the page given URL
        sleep(2)
        response = requests.get(c_url)
        
        # print the response (debugging)
        print(response)
        
        # if status code is = 500, retry
        if response.status_code // 100 == 5:
            continue
        break
        
    # extract the text of the response
    json = response.text
    
    # convert the response's text into Python object
    posts = loads(json)
    
    
    
    for post in posts:
    
        if "id" in post:
            next_id = post["id"]
            break
        
        
    print(next_id)    
    """
    next_id - prints 
    """
    
    y = int(next_id)
    
    x = int(next_id)
    
    for post in posts:
        if "id" not in post:
            continue
        print("ID:", post["id"])
        
        cursor = sqlite.cursor()
        cursor.execute(
            "INSERT or ignore INTO post (id, rating, image_width, image_height) values ({}, '{}', {}, {});".format(
                post["id"],
                post["rating"],
                post["image_width"],
                post["image_height"]
            )
        )
        sqlite.commit()

        image_check = process_post(
            post
        )
        """-----------------------------------------------------------"""
        tags = post["tag_string"]
        post_tags = tags.split( )
        
        
        
        for tag in post_tags:
            
            tag_url = "https://danbooru.donmai.us/tags.json?commit=Search&search%5Bname_or_alias_matches%5D=" + str(tag)
            
            count_cursor = sqlite.cursor()
            entry_count = count_cursor.execute("SELECT id FROM tag WHERE name = '{}'".format(tag.replace("'","''")))
            sqlite.commit()
            counter = entry_count.fetchall()
            
            if len(counter) >= 1:
                continue
            
            sleep(2)
            search_tags = requests.get(tag_url)
            tags_text = search_tags.text
            loads_tags = loads(tags_text)
            
            print("Adding the following tag to the database:", loads_tags[0]["name"])
            
            search_cursor = sqlite.cursor()
            search_cursor.execute(
                "INSERT or ignore INTO tag (id, name, category) values ( {}, '{}', {});".format(
                    loads_tags[0]["id"],
                    loads_tags[0]["name"].replace("'","''"),
                    loads_tags[0]["category"]
                )
            )
            sqlite.commit()
            
        """-----------------------------------------------------------"""
        if not image_check:
            print("Refused to download.")
            print("------------------------")
            continue
        
        print("ID:", post["id"])
        print("Rating", post["rating"])
        print("Image Width:", post["image_width"])
        print("Image Height:", post["image_height"])
        
        sleep(2)
        image_download = requests.get(post["file_url"])
        file_name = "image" + str(post["id"]) + "." + post["file_ext"]
        
        with open(file_name, "wb") as saved_image:
            saved_image.write(image_download.content)
        
        print("Success! Image downloaded.")
        
    if len(posts) < 200: 
        break
        




