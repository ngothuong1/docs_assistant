# Hướng dẫn xin quyền / sử dụng Kafka Auth

# Cluster Dev:

```javascript
Broker: 10.5.93.212:9093,10.5.94.146:9093,10.5.92.188:9093
Version: 3.6.1
Mechanism: SCRAM-SHA-512
Protocol: SASL_PLAINTEXT
Metric: https://metrics.admicro.vn/dashboards/f/e1ebfa8a-6769-4f94-80a8-5779cf209634/kafka-auth-dev
SSL: False
```

# Cluster Production:

```javascript
Broker: kafka-2dc-c2.sys.adt.internal:9093
Version: 3.6.1
Mechanism: SCRAM-SHA-512
Protocol: SASL_PLAINTEXT
Metric: https://metrics.admicro.vn/dashboards/f/b1e98831-10a6-425c-bd5e-ed188e9f333d/kafka-2dc-c2-cluster
SSL: False
```

### IP để test local cho cluster production:

```bash
10.3.68.251
10.5.36.55
10.3.69.166
10.5.36.125
10.3.69.61
10.3.68.124
10.5.37.51
10.3.68.51
10.5.37.189
10.5.36.77
```


# Form xin quyền cơ bản:

```javascript
- Topic Name: topic-name ( không đặt topic có chấm "." hoặc "_"  và 
topic phải đi kèm theo prefix của nhóm. 
Ví dụ ml-service, dw-service, platform-service, adopt-service)
- Retention ( giữ trong bao lâu ) : 1 giờ hoặc 1 ngày
- Cấu hình: Ko biết có thể bỏ qua
- Lượng Request dự kiến: ?? msg/s ( ko biết bỏ qua )
- Size trung bình của message: ?? kb
- Quyền : READ (Consume ) / WRITE ( Produce )
- Description:
+ Service dùng cho bài toán nào?
+ Cho các bên nào dùng:?
- User: Đọc ở dưới
```



1. **Tạo Account mới:**\n- Cần phải có 1 account mới để thực hiện việc authentication vào cluster.\n- Account name nên đặt theo format sau: group-servicename

   Ví dụ: ml-notify-k14\n
2. **Ví dụ về việc xin quyền produce ( write ) vào topic ml-notify-k14**

Chỉ có quyền produce vào 1 topic duy nhất theo như yêu cầu, không có khả năng produce vào các topic khác nếu chưa xin quyền



3. **Ví dụ về việc xin quyền consume ( read ) vào topic ml-notify-k14**

Phần lớn là sử dụng consumer group, việc đặt tên cho consumer-group cũng cần phải theo format như việc đặt tên cho account.

Ví dụ xin quyền read vào consumer group: ml-notify-k14-validation-cg1



4. **Có thể grant topic permission theo prefix. Ví dụ:**\nUser `ml-notify-service` có quyền READ/WRITE đến topic có prefix là:

   `ml-notify-service-*` thì cần grant quyền đúng 1 lần, từ lần sau đi chỉ việc xin tạo topic mới

###