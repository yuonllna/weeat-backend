# Weeat Backend API

맛집 추천 및 리뷰 서비스 백엔드 API

## 🚀 기능

- **장소**: 가게 조회, 카테고리별 필터링
- **리뷰**: 익명 리뷰 작성, 수정, 삭제
- **추천**: 카테고리 중복 없는 랜덤 추천

## 📋 API 엔드포인트

### 장소
- `GET /api/v1/places/` - 가게 조회 (카테고리 필터링 가능)
- `GET /api/v1/places/{place_id}` - 가게 상세 조회
- `GET /api/v1/places/{place_id}/reviews` - 가게 리뷰 조회

### 리뷰
- `POST /api/v1/places/{place_id}/reviews` - 리뷰 작성 (전화번호 필수)
- `PUT /api/v1/places/reviews/{review_id}` - 리뷰 수정
- `DELETE /api/v1/places/reviews/{review_id}` - 리뷰 삭제
- `GET /api/v1/places/reviews/phone/{phone_number}` - 전화번호로 리뷰 조회

### 추천
- `GET /api/v1/recommendations?count=3` - 가게+메뉴 랜덤 추천
