# 修复后的 get_tasks 函数

@app.get("/api/tasks")
async def get_tasks(
    token: str = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user_id: str = None,
    status: str = None,
    channel: str = None,
    task_type: str = None,
    date_range: str = None,
    schedule_name: str = None
):
    """获取任务列表"""
    if not token:
        raise HTTPException(status_code=401, detail="缺少认证 Token")
    if token != DASHBOARD_TOKEN:
        raise HTTPException(status_code=401, detail="Token 无效")
    
    db = get_database()
    await db.connect()
    
    # 构建查询
    query = "SELECT * FROM tasks"
    conditions = []
    params = []
    
    if user_id:
        conditions.append("user_id = ?")
        params.append(user_id)
    if status:
        conditions.append("status = ?")
        params.append(status)
    if channel:
        conditions.append("channel = ?")
        params.append(channel)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    # 执行查询
    async with db._db.execute(query, params) as cursor:
        rows = await cursor.fetchall()
        # 确保转换为字典
        task_list = []
        for row in rows:
            task_dict = dict(row)
            task_list.append(task_dict)
    
    return JSONResponse(content={
        "tasks": task_list,
        "total": len(task_list),
        "limit": limit,
        "offset": offset
    })
