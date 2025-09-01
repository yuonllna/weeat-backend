import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text

async def debug_database():
    """데이터베이스 연결 문제 진단"""
    
    # .env 파일 로드
    load_dotenv()
    
    database_url = os.getenv("DATABASE_URL")
    print("🔍 데이터베이스 연결 진단 시작...")
    print(f"현재 DATABASE_URL: {database_url}")
    print()
    
    if not database_url:
        print("❌ DATABASE_URL이 설정되지 않았습니다.")
        return False
    
    try:
        # 1단계: 엔진 생성 테스트
        print("🔍 1단계: 엔진 생성 테스트...")
        engine = create_async_engine(
            database_url,
            echo=False,
            pool_pre_ping=True,
            pool_size=1,
            max_overflow=0,
            pool_timeout=10
        )
        print("✅ 엔진 생성 성공")
        
        # 2단계: 연결 테스트
        print("\n🔍 2단계: 연결 테스트...")
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1 as test"))
            test_value = result.scalar()
            print(f"✅ 연결 테스트 성공: {test_value}")
        
        # 3단계: 세션 테스트
        print("\n🔍 3단계: 세션 테스트...")
        async with engine.begin() as conn:
            # 데이터베이스 정보 확인
            result = await conn.execute(text("SELECT current_database(), current_user"))
            db_info = result.fetchone()
            print(f"✅ 데이터베이스: {db_info[0]}, 사용자: {db_info[1]}")
            
            # 테이블 목록 확인
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = result.fetchall()
            table_names = [table[0] for table in tables]
            print(f"✅ 테이블 목록: {table_names}")
            
            # places 테이블 데이터 확인
            if 'places' in table_names:
                result = await conn.execute(text("SELECT COUNT(*) FROM places"))
                place_count = result.scalar()
                print(f"✅ places 테이블 데이터: {place_count}개")
                
                if place_count > 0:
                    result = await conn.execute(text("SELECT * FROM places LIMIT 1"))
                    first_place = result.fetchone()
                    print(f"✅ 첫 번째 가게: ID={first_place[0]}, 이름={first_place[1]}")
            else:
                print("❌ places 테이블이 존재하지 않습니다.")
        
        # 4단계: 연결 풀 테스트
        print("\n🔍 4단계: 연결 풀 테스트...")
        for i in range(3):
            try:
                async with engine.begin() as conn:
                    result = await conn.execute(text(f"SELECT {i+1} as test"))
                    test_value = result.scalar()
                    print(f"   연결 {i+1}: {test_value}")
            except Exception as e:
                print(f"   연결 {i+1} 실패: {e}")
        
        await engine.dispose()
        print("\n✅ 모든 테스트 통과!")
        return True
        
    except Exception as e:
        print(f"❌ 진단 실패: {e}")
        print(f"오류 타입: {type(e).__name__}")
        return False

if __name__ == "__main__":
    asyncio.run(debug_database())
