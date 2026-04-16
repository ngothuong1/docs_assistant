# Hướng dẫn xin quyền Elasticsearch

Thông tin cụm ES 8 Dev:

```javascript
Host: "10.3.104.45", "10.5.92.32", "10.5.94.219", "10.5.92.224", "10.3.105.206", "10.3.104.158"
Port: 9200
Version: 8.8.1
Kibana: http://10.3.105.14:5601/
Metric: https://metrics.admicro.vn/d/JsU2B0z7k/elasticsearch-latest?orgId=1&var-server=000000001&var-cluster=adt-sys-es8-dev
```


Thông tin cụm ES 8 Prod:

```javascript
Host: "10.3.69.161", "10.5.38.176", "10.3.69.247", "10.5.38.44", "10.3.69.18", "10.3.68.132", "10.5.38.66", "10.3.68.60", "10.5.37.154", "10.3.69.110", "10.5.38.52", "10.5.38.159"
Port: 9200
Version: 8.8.2
Kibana: http://10.3.68.132:5601/
Metric: https://metrics.admicro.vn/d/JsU2B0z7k/elasticsearch-latest?orgId=1&var-server=000000001&var-cluster=adt-sys-es8-c1
```


Ví dụ xin tạo index mới Elasticsearch

```javascript
- Index name: ví dụ cho index name ml-kenh14-notify / platform-brandsafety / dw-money-charger
- Document size trung bình: 
- Lương document đẩy vào trong 1 ngày / 1 tháng / 1 năm: 
- Lưu theo tháng / năm hay chỉ 1 index?:  phụ thuộc vào số lượng document đẩy vào ở trên
- Lưu trữ vĩnh viễn hay chỉ cần giữ lại mấy tháng gần đây nhất, nêu có thì là mấy tháng. ( Lưu ý: nếu lưu trữ vĩnh viễn và lưu trữ theo tháng thì yêu cầu sau mỗi năm 12 index theo tháng sẽ được gộp lại thành 1 index theo năm )
- Tạo account: group-service-name ( ví dụ, ml-search-data / crawler-data-cdp )
```


Cách tính document, ví dụ ghi log lỗi, ko rõ lỗi nhiều hay ít. Tính khoảng min và max. Sai số trong mức chấp nhận được là 20-30% lượng log 1 ngày.