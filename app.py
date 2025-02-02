from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# TMDB API 키
TMDB_API_KEY = ''

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    print(1)
    media_data = None  # 영화 또는 드라마 정보를 저장하는 변수
    search_type = None
    if request.method == 'POST':
        search_query = request.form['search_query']
        search_type = request.form['search_type']  # 사용자가 선택한 검색 유형 (영화 또는 드라마)

        # 검색 유형에 따라 TMDB API에서 영화 또는 드라마 정보를 검색 (한국어로 설정)
        url = f'https://api.themoviedb.org/3/search/{search_type}?api_key={TMDB_API_KEY}&query={search_query}&language=ko-KR'
        response = requests.get(url)
        data = response.json()
       
        if data.get('results'):
            media_data = data['results']
                   

    return render_template('search.html', media_data=media_data, search_type=search_type)

@app.route('/detail/<genre>/<int:media_id>')
def detail(media_id, genre):
    # 상세 정보를 가져오기 위한 TMDB API 요청
    url = f'https://api.themoviedb.org/3/{genre}/{media_id}?api_key={TMDB_API_KEY}&language=ko-KR'
    response = requests.get(url)
    media_detail = response.json()
    # OTT 플렛폼 가져오는 API 요청
    url = f'https://api.themoviedb.org/3/{genre}/{media_id}/watch/providers?api_key={TMDB_API_KEY}'
    print(url)
    response = requests.get(url)
    ott_data = response.json()
    platforms = []
    # OTT 플랫폼 정보가 있는 경우, 구매, 대여, 정액제 정보를 추출
    if ott_data.get('results') and ott_data['results'].get('KR'):
        kr_data = ott_data['results']['KR']

        if kr_data.get('buy'):
            platforms.append({'type': '구매', 'providers': kr_data['buy']})
        if kr_data.get('rent'):
            platforms.append({'type': '대여', 'providers': kr_data['rent']})
        if kr_data.get('flatrate'):
            platforms.append({'type': '정액제', 'providers': kr_data['flatrate']})
            
    # 메인 예고편, 티저 등 동영상 정보를 가져오는 API 요청
    url = f'https://api.themoviedb.org/3/{genre}/{media_id}/videos?api_key={TMDB_API_KEY}&language=ko-KR'
    response = requests.get(url)
    media_video = response.json()
    # 동영상 키 추출 (예고편 또는 티저 정보가 있는 경우)
    video_key = None
    if media_video.get('results'):
        for video in media_video['results']:
            if video['type'] == 'Trailer' and video['site'] == 'YouTube':
                video_key = video['key']
                break
            
            elif video['type'] == 'Teaser' and video['site'] == 'YouTube':
                video_key = video['key']
                break
    print(video_key)
    return render_template('detail.html', media_detail=media_detail ,genre=genre, providers = platforms, video_key=video_key)

if __name__ == '__main__':
    app.run(debug=True)
