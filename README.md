# Weeat Backend API

맛집 추천 및 리뷰 서비스 백엔드 API

## 🚀 기능

- **인증**: 이메일 회원가입/로그인, 카카오/구글 소셜 로그인
- **장소**: 가게 조회, 카테고리별 필터링
- **리뷰**: 리뷰 작성, 수정, 삭제
- **추천**: 카테고리 중복 없는 랜덤 추천

## 📋 API 엔드포인트

### 인증
- `POST /api/v1/auth/email/sign-up` - 이메일 회원가입
- `POST /api/v1/auth/email/sign-in` - 이메일 로그인
- `POST /api/v1/auth/kakao/sign-in` - 카카오 소셜 로그인
- `POST /api/v1/auth/google/sign-in` - 구글 소셜 로그인
- `DELETE /api/v1/auth/user` - 회원 탈퇴
- `POST /api/v1/auth/user/revoke-social` - 소셜 계정 연결 해제

### 장소
- `GET /api/v1/places/` - 가게 조회 (카테고리 필터링 가능)
- `GET /api/v1/places/{place_id}` - 가게 상세 조회
- `GET /api/v1/places/{place_id}/reviews` - 가게 리뷰 조회

### 리뷰
- `POST /api/v1/places/{place_id}/reviews` - 리뷰 작성
- `PUT /api/v1/places/reviews/{review_id}` - 리뷰 수정
- `DELETE /api/v1/places/reviews/{review_id}` - 리뷰 삭제

### 추천
- `GET /api/v1/recommendations?count=3` - 가게+메뉴 랜덤 추천
