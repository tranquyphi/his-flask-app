"""
Tests API endpoints - FastAPI version
Basic CRUD operations for medical tests management
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Import database models and session
from models_main import get_db
from models.Test import Test

# Create router with /api prefix
router = APIRouter(prefix="/api", tags=["Tests"])

# Pydantic models
class TestResponse(BaseModel):
    TestId: str
    TestName: str
    TestGroup: Optional[str] = None
    TestPriceBHYT: Optional[int] = None
    TestPriceVP: Optional[int] = None
    TestAvailable: Optional[bool] = True
    TestNote: Optional[str] = None
    TestType: Optional[str] = None
    InChargeDepartmentId: Optional[int] = None

class TestCreate(BaseModel):
    TestId: str
    TestName: str
    TestGroup: Optional[str] = None
    TestPriceBHYT: Optional[int] = None
    TestPriceVP: Optional[int] = None
    TestAvailable: Optional[bool] = True
    TestNote: Optional[str] = None
    TestType: Optional[str] = None
    InChargeDepartmentId: Optional[int] = None

@router.get("/tests", response_model=dict)
async def list_tests(
    test_type: Optional[str] = Query(None, description="Filter by test type (XN, SA, XQ, CT, TDCN, NS)"),
    available_only: Optional[bool] = Query(None, description="Show only available tests"),
    db: Session = Depends(get_db)
):
    """Get all tests with optional filters"""
    try:
        query = db.query(Test)
        
        if test_type:
            query = query.filter(Test.TestType == test_type)
            
        if available_only:
            query = query.filter(Test.TestAvailable == True)
        
        tests = query.all()
        result = []
        for test in tests:
            test_dict = {
                'TestId': test.TestId,
                'TestName': test.TestName,
                'TestGroup': test.TestGroup,
                'TestPriceBHYT': test.TestPriceBHYT,
                'TestPriceVP': test.TestPriceVP,
                'TestAvailable': test.TestAvailable,
                'TestNote': test.TestNote,
                'TestType': test.TestType,
                'InChargeDepartmentId': test.InChargeDepartmentId
            }
            result.append(test_dict)
        return {'tests': result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tests/{test_id}", response_model=dict)
async def get_test(test_id: str, db: Session = Depends(get_db)):
    """Get a specific test by ID"""
    try:
        test = db.query(Test).get(test_id)
        if not test:
            raise HTTPException(status_code=404, detail="Test not found")
        
        test_dict = {
            'TestId': test.TestId,
            'TestName': test.TestName,
            'TestGroup': test.TestGroup,
            'TestPriceBHYT': test.TestPriceBHYT,
            'TestPriceVP': test.TestPriceVP,
            'TestAvailable': test.TestAvailable,
            'TestNote': test.TestNote,
            'TestType': test.TestType,
            'InChargeDepartmentId': test.InChargeDepartmentId
        }
        return {'test': test_dict}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tests", response_model=dict)
async def create_test(test_data: TestCreate, db: Session = Depends(get_db)):
    """Create a new test"""
    try:
        new_test = Test(
            TestId=test_data.TestId,
            TestName=test_data.TestName,
            TestGroup=test_data.TestGroup,
            TestPriceBHYT=test_data.TestPriceBHYT,
            TestPriceVP=test_data.TestPriceVP,
            TestAvailable=test_data.TestAvailable,
            TestNote=test_data.TestNote,
            TestType=test_data.TestType,
            InChargeDepartmentId=test_data.InChargeDepartmentId
        )
        
        db.add(new_test)
        db.commit()
        db.refresh(new_test)
        
        test_dict = {
            'TestId': new_test.TestId,
            'TestName': new_test.TestName,
            'TestGroup': new_test.TestGroup,
            'TestPriceBHYT': new_test.TestPriceBHYT,
            'TestPriceVP': new_test.TestPriceVP,
            'TestAvailable': new_test.TestAvailable,
            'TestNote': new_test.TestNote,
            'TestType': new_test.TestType,
            'InChargeDepartmentId': new_test.InChargeDepartmentId
        }
        
        return {'test': test_dict, 'message': 'Test created successfully'}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
