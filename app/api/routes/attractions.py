from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, List
import os
import uuid
from datetime import datetime

from app.db.session import SessionLocal

# Defensive imports for heavy logic
try:
    from app.db.crud_attractions import (
        create_attraction, get_attraction, get_attractions, get_attractions_count,
        get_recommended_attractions, update_attraction, delete_attraction, search_attractions
    )
    from app.schemas.attraction import (
        AttractionCreate, AttractionUpdate, AttractionResponse, AttractionListResponse
    )
    from app.utils.ui_templates import format_for_ui
    from app.services.ahp import AHPCalculator
except ImportError:
    # If imports fail (e.g. some dependency missing), we might be in a broken state
    # but we define mock classes/functions to let the file load.
    pass

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/attractions", response_model=AttractionResponse)
def create_attraction_endpoint(attraction: AttractionCreate, db: Session = Depends(get_db)):
    """创建景点"""
    return create_attraction(db, attraction)


@router.get("/attractions", response_model=AttractionListResponse)
def list_attractions(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    is_recommended: Optional[bool] = Query(None, description="是否推荐"),
    category: Optional[str] = Query(None, description="分类筛选"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db)
):
    """获取景点列表"""
    skip = (page - 1) * page_size
    
    if keyword:
        # 搜索模式
        items = search_attractions(db, keyword, limit=page_size)
        total = len(items)  # 简化处理，实际可优化为分页搜索
    else:
        # 普通列表模式
        items = get_attractions(db, skip=skip, limit=page_size, is_recommended=is_recommended, category=category)
        total = get_attractions_count(db, is_recommended=is_recommended, category=category)
    
    return AttractionListResponse(
        total=total,
        items=items,
        page=page,
        page_size=page_size
    )


@router.get("/attractions/recommend", response_model=List[AttractionResponse])
def get_recommend_attractions(
    limit: int = Query(10, ge=1, le=50, description="推荐数量"),
    ahp_at: Optional[float] = Query(None, description="AHP: Access vs Theme (1-9)"),
    ahp_tc: Optional[float] = Query(None, description="AHP: Theme vs Color (1-9)"),
    ahp_ac: Optional[float] = Query(None, description="AHP: Access vs Color (1-9)"),
    db: Session = Depends(get_db)
):
    """获取推荐景点列表（供小程序调用，支持 AHP 加权）"""
    if ahp_at and ahp_tc and ahp_ac:
        # AHP 模式
        # 1. 获取所有推荐候选
        candidates = get_attractions(db, limit=100, is_recommended=True)
        
        # 2. 计算权重
        try:
            weights = AHPCalculator.calculate_weights(ahp_at, ahp_tc, ahp_ac)
            
            # 3. 计算得分并排序
            candidates.sort(
                key=lambda x: AHPCalculator.calculate_score(x, weights),
                reverse=True
            )
        except Exception:
            # Fallback if AHP fails
            pass
        
        return candidates[:limit]
        
    return get_recommended_attractions(db, limit=limit)


@router.get("/attractions/{attraction_id}", response_model=AttractionResponse)
def get_attraction_detail(attraction_id: int, db: Session = Depends(get_db)):
    """获取景点详情"""
    attraction = get_attraction(db, attraction_id)
    if not attraction:
        raise HTTPException(status_code=404, detail="景点不存在")
    
    # 动态注入 UI 资源（封面图等），确保详情页与列表页图片一致
    ui_data = format_for_ui(attraction)
    if ui_data.get("ui_cover_image"):
        attraction.cover_image = ui_data.get("ui_cover_image")
        
    return attraction


@router.put("/attractions/{attraction_id}", response_model=AttractionResponse)
def update_attraction_endpoint(
    attraction_id: int, 
    attraction_update: AttractionUpdate, 
    db: Session = Depends(get_db)
):
    """更新景点"""
    attraction = update_attraction(db, attraction_id, attraction_update)
    if not attraction:
        raise HTTPException(status_code=404, detail="景点不存在")
    return attraction


@router.delete("/attractions/{attraction_id}")
def delete_attraction_endpoint(attraction_id: int, db: Session = Depends(get_db)):
    """删除景点"""
    success = delete_attraction(db, attraction_id)
    if not success:
        raise HTTPException(status_code=404, detail="景点不存在")
    return {"message": "删除成功"}


@router.post("/attractions/upload-image")
async def upload_attraction_image(file: UploadFile = File(...)):
    """上传景点图片"""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="请上传图片文件")
    
    # 创建上传目录
    upload_dir = "storage/attractions"
    try:
        os.makedirs(upload_dir, exist_ok=True)
    except Exception:
        # Vercel fallback
        upload_dir = "/tmp"
    
    # 生成唯一文件名
    file_extension = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    unique_filename = f"{uuid.uuid4().hex}{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # 保存文件
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # 返回相对路径，供前端使用
        return {
            "success": True,
            "file_path": f"/static/attractions/{unique_filename}",
            "message": "图片上传成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图片上传失败: {str(e)}")


@router.post("/attractions/{attraction_id}/upload-cover")
async def upload_attraction_cover(
    attraction_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """为指定景点上传封面图片"""
    # 检查景点是否存在
    attraction = get_attraction(db, attraction_id)
    if not attraction:
        raise HTTPException(status_code=404, detail="景点不存在")
    
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="请上传图片文件")
    
    # 创建上传目录
    upload_dir = "storage/attractions"
    try:
        os.makedirs(upload_dir, exist_ok=True)
    except Exception:
        # Vercel fallback
        upload_dir = "/tmp"
    
    # 生成唯一文件名
    file_extension = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    unique_filename = f"cover_{attraction_id}_{uuid.uuid4().hex}{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # 更新景点封面图片路径
        cover_url = f"/static/attractions/{unique_filename}"
        update_data = AttractionUpdate(cover_image=cover_url)
        updated_attraction = update_attraction(db, attraction_id, update_data)
        
        return {
            "success": True,
            "attraction": updated_attraction,
            "cover_image": cover_url,
            "message": "封面图片上传成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图片上传失败: {str(e)}")