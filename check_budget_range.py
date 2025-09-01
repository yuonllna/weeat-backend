import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def check_budget_range():
    """데이터베이스에 budget_range 컬럼이 있는지 확인"""
    
    # .env 파일 로드
    load_dotenv()
    
    database_url = os.getenv("DATABASE_URL")
    print("🔍 budget_range 컬럼 확인 시작...")
    print(f"현재 DATABASE_URL: {database_url}")
    print()
    
    if not database_url:
        print("❌ DATABASE_URL이 설정되지 않았습니다.")
        return False
    
    try:
        engine = create_async_engine(
            database_url,
            echo=False,
            pool_pre_ping=True,
            pool_size=1,
            max_overflow=0,
            pool_timeout=10
        )
        
        async with engine.begin() as conn:
            # places 테이블의 컬럼 정보 확인
            result = await conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'places' 
                ORDER BY ordinal_position
            """))
            
            columns = result.fetchall()
            print("📋 places 테이블 컬럼 목록:")
            for col in columns:
                print(f"  - {col[0]} ({col[1]}, nullable: {col[2]})")
            
            # budget_range 컬럼 존재 여부 확인
            budget_range_exists = any(col[0] == 'budget_range' for col in columns)
            
            if budget_range_exists:
                print("\n✅ budget_range 컬럼이 존재합니다!")
                
                # budget_range 컬럼의 데이터 샘플 확인
                result = await conn.execute(text("SELECT DISTINCT budget_range FROM places WHERE budget_range IS NOT NULL LIMIT 5"))
                sample_values = result.fetchall()
                print(f"   샘플 값들: {[row[0] for row in sample_values]}")
                
            else:
                print("\n❌ budget_range 컬럼이 존재하지 않습니다.")
                print("💡 데이터베이스에 budget_range 컬럼을 추가해야 합니다.")
            
            await engine.dispose()
            return budget_range_exists
            
    except Exception as e:
        print(f"❌ 확인 실패: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(check_budget_range())
