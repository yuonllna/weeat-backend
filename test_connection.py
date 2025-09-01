import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text  # 추가
from dotenv import load_dotenv


async def test_simple_connection():
    """간단한 데이터베이스 연결 테스트"""
    
    # .env 파일 로드
    load_dotenv()
    
    # 환경 변수에서 DATABASE_URL 가져오기
    database_url = os.getenv("DATABASE_URL")
    
    print("🔍 데이터베이스 연결 테스트 시작...")
    print("현재 환경변수 DATABASE_URL:", database_url if database_url else "설정되지 않음")
    print()
    
    if not database_url:
        print("❌ DATABASE_URL이 설정되지 않았습니다.")
        print("💡 .env 파일에 DATABASE_URL을 설정해주세요.")
        return None
    
    try:
        print(f"🔍 연결 시도: {database_url}")
        engine = create_async_engine(database_url, echo=False)
        
        async with engine.begin() as conn:
            # text() 함수로 감싼 쿼리 실행
            result = await conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            if row and row.test == 1:
                print(f"✅ 연결 성공!")
                
                # 데이터베이스 정보 확인
                result = await conn.execute(text("SELECT current_database(), current_user"))
                db_info = result.fetchone()
                print(f"   데이터베이스: {db_info[0]}, 사용자: {db_info[1]}")
                
                # 테이블 목록 확인
                try:
                    result = await conn.execute(text("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                        ORDER BY table_name
                    """))
                    tables = result.fetchall()
                    print(f"   테이블 목록: {[table[0] for table in tables]}")
                    
                    # places와 menus 테이블이 있는지 확인
                    table_names = [table[0] for table in tables]
                    if 'places' in table_names:
                        print("   ✅ places 테이블 존재")
                    else:
                        print("   ❌ places 테이블 없음")
                        
                    if 'menus' in table_names:
                        print("   ✅ menus 테이블 존재")
                    else:
                        print("   ❌ menus 테이블 없음")
                        
                except Exception as e:
                    print(f"   테이블 목록 조회 실패: {e}")
                
                await engine.dispose()
                return database_url
                
    except Exception as e:
        print(f"❌ 연결 실패: {e}")
        print("\n💡 해결 방법:")
        print("1. PostgreSQL이 실행 중인지 확인: services.msc")
        print("2. .env 파일의 DATABASE_URL 형식 확인")
        print("3. 데이터베이스 이름, 사용자명, 비밀번호 확인")
        return None


if __name__ == "__main__":
    asyncio.run(test_simple_connection())
