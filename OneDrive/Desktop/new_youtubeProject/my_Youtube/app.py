from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
from bson import ObjectId



# 전체 동영상 갯수 변경 여부 및 추가된 영상의 제목을 체크
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from conf import youtube_api_key
import time
from datetime import datetime
import pymongo


now = datetime.now()

app = Flask(__name__)

client = MongoClient("localhost", 27017)

db = client['youtube_db']
collection = db['youtube_collection']
# db_youtube = client.youtube_collection # 저번에 이렇게 썼엇는데 일단 보류해보자

# db = client['your_database']  # 여기서 'your_database'를 실제 MongoDB 데이터베이스 이름으로 변경하세요
# collection = db['your_collection']  # 'your_collection'을 실제 컬렉션 이름으로 변경하세요


###############################
# 보안이 중요한 부분
youtube = build("youtube", "v3", " 빈칸 ")
channel_id = " 빈칸 " # 넣을 채널의 id 입력 내채력인지 확인하고자 할 채널인지
###############################

try:
    #최신 동영상 목록 가져오기
    request = youtube.search().list(
        part = "id,snippet",
        channelID = channel_id,
        order = "data",
        type = "video",
        maxResults=5 ## 가져올 최대 비디오 갯수 
    ).execute()
    
    video_count = 0
    
    # 동영상 제목과 링크 출력
    for video in request["items"]: # items 를 순환 시키고 # 각 값에 맞춰 지정
        video_id = video["id"]["videoId"]
        title = video["snippet"]["title"]
        url = f"https://www.youtube.com/watch?v={video_id}"
        published_at = video["snippet"]["publishedAt"] # 동영상 업로드 날짜 가져오기
        
        if "short" not in title.lower():
            print(f"Title : {title}")
            
            #mongoDB에 넣기
            video_doc = {
                "video_id": video_id,
                "title" : title,
                "url" : url,
                "published_at" : published_at
            }
            collection.insert_one(video_doc) # video_doc 라는것을 만들어서 collection 데이터 넣기
            
            if collection.count_documents({"video_id": video_id}) == 0:
                collection.insert_one(video_doc)
                print(f"New Video added (새로운 비디오 들어감) : {title}")
            else:
                print(f"video already exists (이미 존재하는 비디오) {title}")
                
except Exception as e:
    print(f"\n-----------------\nAn error occurred \n------에러가 떴띠야----------------\n 원인 : {e}\n ----------------------------------")

# 데이터를 삽입한 날짜 넣는것
def insert_video_to_mongodb(video_id, title, url, published_at):
    db.youtube_collection.insert_one({
        "video_id" : video_id,
        "title" : title,
        "url" : url,
        "published_at" : published_at,
        "inserted_at" : now
    })
    print(f"{now} 에 추가 된 비디오 {title}")
    
# 최신 동영상 링크 추출




@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get_data", methods=['GET'])
def get_data():
    #mongoDB에서 데이터 가져오기
    data = list(collection.find({}, {'_id':0})) # _id 필드는 제외하고 모든 필드를 가져 옵니다
    return jsonify(data)

# if __name__ == '__main__':
#     app.run('0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    app.run(debug=True)