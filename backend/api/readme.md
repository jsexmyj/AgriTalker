routers:
    api 路由定义，参考study的项目代码
    包含上传文件、查询进度、获取瓦片结果等接口

    POST /upload — 上传 GeoTIFF，返回 file_id,file_url
    (待定）POST /task — 创建处理任务（body: file_id, ops: [{type:"crop", bbox:...}, {type:"ndvi", tile_ids:...}]) -> 返回 task_id

    GET /task/{task_id}/status — 查询进度与日志片段
    GET /outputs/对应文件下 - 获取切片结果 静态服务
    POST /chat 接受用户的消息

schemas:
    存放接口参数定义