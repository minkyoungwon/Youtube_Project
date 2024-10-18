
# 전체 동영상 갯수 변경 여부 및 추가된 영상의 제목을 체크
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
# youtube data api의 api key 를 입력합니다
from conf import youtube_api_key

import time
from datetime import datetime
import pymongo

# monogDB 클라이언트 설정
client = pymongo.MongoClient("localhost", 27017) # 로컬 mongodb 서버 연결
db = client.youtube_db # youtube_db 라는 데이터베이스 선택
collection = db.youtube_collection # video 라는 컬렉션 선택
 
 # now = 현재 날짜와 시간을 출력
now = datetime.now()




# # 텔레그램 # 설치해야함
import telegram

# 텔레그램 메신저를 사용하기 위한 토큰 설정 부분
# bot = telegram.Bot(token="") # 텔레그램 토근 받아와서 넣기


# youtube data api 를 사용하기 위한 준비
youtube = build("youtube", "v3", developerKey=" 쉿 비밀이에요")

# 채널 id 를 입력합니다
# channel_id = "UC4uGVGxC9kiYkLBnU1a97Vw" #아영이네
# 민경원 채널로 바꿀 경우 = UCsIBGQlJLZhJU-OfJhCCkbg 이걸로 바꾸면 됨 // 일단 테스트는 이걸로 하는쪽으로 하샘
channel_id = "UCsIBGQlJLZhJU-OfJhCCkbg" # 민경원 채널

try:
    #최신 동영상 목록 가져오기
    request = youtube.search().list(
        part="id,snippet",
        channelId=channel_id,
        order="date",
        type="video",
        maxResults=5
    ).execute()
    
    video_count = 0
    
    # 동영상 제목과 링크 출력
    for video in request["items"]:
        video_id = video["id"]["videoId"]
        title = video["snippet"]["title"]
        url = f"https://www.youtube.com/watch?v={video_id}"
        published_at = video["snippet"]["publishedAt"] # 동영상 업로드 날짜 가져오기
        
        if "short" not in title.lower():
            # print(f"Title: {title}\nURL: {url}\n published_at: {published_at}") # 제목 url 날짜 출력
            print(f"Title: {title}")
            
            # mongodb에 넣기
            video_doc = {
                "video_id": video_id,
                "title": title,
                "url": url,
                "published_at": published_at
            }
            collection.insert_one(video_doc)
            
            
            if collection.count_documents({"video_id": video_id}) == 0:
                collection.insert_one(video_doc)
                print(f"New video added (새로운 비디오 들감): {title}")
            else:
                print(f"Video already exists (이미 존재하는 비디오): {title}")
            
except Exception as e:
    print(f"An error occurred: {e}")


# mongodb에 넣어서 사용하기
# youtube_collection 이라는 컬렉션에 넣기 (youtube이라는 컬렉션이 없어서
# 그냥 바로 insert_one 해서 넣으면 넣어짐)

# 데이터를 삽입한 날짜도 넣자
def insert_video_to_mongodb(video_id, title, url, published_at):
    db.youtube_collection.insert_one({
        "video_id": video_id, "title": title, "url": url, "published_at": published_at, "inserted_at": now
        })
    print(f"{now} 에 추가된 비디오 {title}")

# 최신 동영상 링크 추출
def get_latest_video_link(channel_id):
    youtube = build("youtube", "v3", developerKey=" 쉿 비밀임")
    request = youtube.search().list(
        part="id,snippet",
        channelId=channel_id,
        order="date",
        type="video",
        maxResults=1
    ).execute()
    return request["items"][0]["id"]["videoId"]


# 텔레그램 전달 코드
# 만들려다가 귀찮아서 보류중.... 



if __name__ == "__main__":
    # 기존의 비디오 콜렉션 삭제
    #db.youtube_collection.drop() #이걸 해버리면 기존에 있던걸 전부다 삭제해버리는 것임
    
    # 새로운 비디오 추가
    insert_video_to_mongodb(video_id, title, url, published_at)

print(get_latest_video_link(channel_id))





 


# 이전에 짯던 코드들


# 쇼츠를 제외한 영상을 추출하는 코드
# try:
#     # 최신 동영상 목록 가져오기
#     request = youtube.search().list(
#         part="id,snippet",
#         channelId=channel_id,
#         order="date",
#         type="video",
#         maxResults=10  # 원하는 개수로 설정 가능
#     ).execute()

#     video_count = 0

#     # 동영상 제목과 링크를 출력
#     for video in request["items"]:
#         video_id = video["id"]["videoId"]
#         title = video["snippet"]["title"]
#         url = f"https://www.youtube.com/watch?v={video_id}"
        
#         if "short" not in title.lower(): # 대소문자 구분 없이 검사
#             print(f"Title: {title}\nURL: {url}\n")
#             video_count += 1
#         else:
#             print("short 동영상 제외")
            
#         # 5개의 비short 동영상 추출시 종료
#         if video_count == 5:
#             break
        
        
# except Exception as e:
#     print(f"An error occurred: {e}")
    
# print("===============")

# 쇼츠를 제외한 올라온 동영상이 오늘 날짜 일 경우 영상을 추출


