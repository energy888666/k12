from django.utils.deprecation import MiddlewareMixin
class CorsMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # 给响应头加上 Access-Control-Allow-Origin 字段 并简单的设置为 *
        response['Access-Control-Allow-Origin'] = '*'
        if request.method == 'OPTIONS':
            # 允许发送 PUT 请求
            response['Access-Control-Allow-Methods'] = 'PUT, DELETE'
            # 允许在请求头中携带 Content-type字段，从而支持发送json数据
            response['Access-Control-Allow-Headers'] = 'Content-type'
        return response