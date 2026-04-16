# Hướng dẫn sử dụng API Gateway Dashboard

# Hướng dẫn sử dụng API Gateway Dashboard

### Các khái niệm

* **Service** Khai báo các thông tin về backend service: backend host, timeout...
* **Route** Khai báo các thông tin để public ra: path, method...
* **Upstream** Khai báo load balancing cho backend
* **Consumer** Quản lý các thông tin về auth key, jwt, hmac...
* Hệ thống bao gồm nhiều Team. Mỗi team sẽ được cấp 1 suffix API để public riêng Ví dụ: Team Analytics -> http://192.168.1.2:8000/analytics/ Team Platform -> http://192.168.1.2:8000/platform/
* **Leader**: Full quyền (tạo, sửa, xoá service/upstream/consumer...)
* **Owner**: Full quyền trên service/upstream/consumer mà mình tạo
* **Editor**: Trong 1 team có thể có nhiều người cùng phát triển 1 API/Service. Owner có thể add thêm các user khác vào làm Editor của 1 service/upstream/consumer. Editor chỉ có quyền edit, không có quyền xoá.

### Hướng dẫn chi tiết

* **Quản lý service**: [\[API Gateway Dashboard\] Quản lý service](/doc/api-gateway-dashboard-quan-ly-service-JjvLVmMNmQ)
* **Quản lý upstream**: [\[API Gateway Dashboard\] Quản lý upstream](/doc/api-gateway-dashboard-quan-ly-upstream-0AWpXGDJwq)
* **Quản lý Plugin**: [\[API Gateway Dashboard\] Quản lý plugin](/doc/api-gateway-dashboard-quan-ly-plugin-19CBnndmbB)
* **Quản lý Consumer**: [\[API Gateway Dashboard\] Quản lý consumer](/doc/api-gateway-dashboard-quan-ly-consumer-KDeUkVuEWf)