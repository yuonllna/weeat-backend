import httpx
import json
from typing import Optional, Dict, Any
from google.auth.transport import requests
from google.oauth2 import id_token
from google.auth.exceptions import GoogleAuthError
from fastapi import HTTPException, status
import os

# 환경 변수에서 클라이언트 ID 가져오기
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "your-google-client-id")

class OAuthVerifier:
    """OAuth 토큰 검증 클래스"""
    
    @staticmethod
    async def verify_kakao_token(access_token: str) -> Optional[Dict[str, Any]]:
        """카카오 액세스 토큰 검증 및 사용자 정보 조회"""
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            async with httpx.AsyncClient() as client:
                # 카카오 사용자 정보 조회
                response = await client.get(
                    "https://kapi.kakao.com/v2/user/me",
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    user_data = response.json()
                    return {
                        "auth_provider": "kakao",
                        "auth_sub": str(user_data["id"]),
                        "display_name": user_data["properties"]["nickname"],
                        "email": user_data.get("kakao_account", {}).get("email"),
                        "profile_image": user_data["properties"].get("profile_image")
                    }
                else:
                    return None
                    
        except Exception as e:
            print(f"Kakao token verification error: {e}")
            return None
    
    @staticmethod
    async def verify_google_token(id_token_str: str) -> Optional[Dict[str, Any]]:
        """구글 ID 토큰 검증 및 사용자 정보 조회"""
        try:
            # 구글 ID 토큰 검증
            idinfo = id_token.verify_oauth2_token(
                id_token_str, 
                requests.Request(), 
                GOOGLE_CLIENT_ID
            )
            
            # 토큰이 유효한지 확인
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                return None
            
            return {
                "auth_provider": "google",
                "auth_sub": idinfo["sub"],
                "display_name": idinfo.get("name", ""),
                "email": idinfo.get("email"),
                "profile_image": idinfo.get("picture")
            }
            
        except GoogleAuthError as e:
            print(f"Google token verification error: {e}")
            return None
        except Exception as e:
            print(f"Google token verification error: {e}")
            return None

# 편의 함수들
async def verify_social_token(provider: str, token: str) -> Optional[Dict[str, Any]]:
    """소셜 로그인 토큰 검증"""
    if provider == "kakao":
        return await OAuthVerifier.verify_kakao_token(token)
    elif provider == "google":
        return await OAuthVerifier.verify_google_token(token)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"지원하지 않는 소셜 로그인: {provider}"
        )

async def revoke_social_connection(provider: str, access_token: str) -> bool:
    """소셜 계정 연결 해제"""
    try:
        if provider == "kakao":
            # 카카오 연결 해제
            headers = {"Authorization": f"Bearer {access_token}"}
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://kapi.kakao.com/v1/user/unlink",
                    headers=headers,
                    timeout=10.0
                )
                return response.status_code == 200
                
        elif provider == "google":
            # 구글 연결 해제 (구글은 별도 API 없음)
            # 구글 계정 설정에서 수동으로 해제 필요
            return True
            
        return False
    except Exception as e:
        print(f"Social connection revocation error: {e}")
        return False
