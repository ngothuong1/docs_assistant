# Hướng dẫn sử dụng Clickhouse cluster

* Tạo table: Gửi issue redmine với yêu cầu tạo bảng clickhouse cho database 'db_name' \nNội dung là query tạo bảng

  ```javascript
  CREATE TABLE db_name.table_name ON CLUSTER cluster_name
  (
      `id` UInt64,
      `column1` String
  )
  ORDER BY id
  ```

  `ENGINE, SETTINGS, cluster_name` sẽ do phía sysadmin set


* Xin quyền: 1 user truy cập được tất cả mọi nơi.\nXin tạo user service: `ml_notify_k14` với quyền `select,insert,update,delete` trên `db_name.table_name`


Ví dụ thực tế: <https://redmine.admicro.vn/issues/32066>

```javascript
create user notification_log on cluster cluster_1S_2R_1 identified by 'pass_plaintext_here';
```

```javascript
CREATE TABLE database_name.ml_notify_logs ON CLUSTER cluster_1S_2R_1

(

    notification_id String,

    post_id         String,

    user_id         String,

    device_id       String,

    order_id        Int64,

    group_id        Int16,

    event           Int8,

    breaking_news   Int8,

    type            Int8,

    sub_type        Int16,

    content_type    Int8,

    news_type       String,

    from            String,

    create_time     DateTime,

    update_time     DateTime,

    is_push         Bool,

    is_persist      Bool,

    app_name        String,

    agent_id        Int32 default -1,

    source_id       Int32 default -1

) 

ENGINE = ReplicatedMergeTree 

        PRIMARY KEY (app_name, order_id, update_time, event)

        ORDER BY (app_name, order_id, update_time, event)

        SETTINGS storage_policy = 'multiple_disks';
```


```javascript
GRANT ON CLUSTER cluster_1S_2R_1 SELECT, INSERT, ALTER UPDATE, ALTER DELETE ON ml_notification_db.ml_notify_logs TO notification_log;
```


# Drop table on cluster:

```javascript
drop table ml_notification_db.ml_notify_logs on cluster cluster_1S_2R_1;
```

# Get the top 20 largest tables

```sql
SELECT
    database,
    table,
    formatReadableSize(SUM(bytes_on_disk)) AS size_on_disk,
    SUM(rows) AS total_rows
FROM system.parts
WHERE active = 1
GROUP BY database, table
ORDER BY SUM(bytes_on_disk) DESC
LIMIT 20;
```

# Reclaim disk space by deleting the detached parts

### Get detached parts that are safe to drop

```bash
clickhouse-client --query="
SELECT concat(
    'ALTER TABLE ', database, '.', table,
    ' DROP DETACHED PART ''', name, ''';'
)
FROM system.detached_parts
WHERE reason NOT IN ('Broken', 'Unexpected');
" --format=TSVRaw > drop_detached_parts.sql
```

### Enable DROP DETACHED

Create file `/etc/clickhouse-server/users.d/query.settings.xml` with the following content if it does not exist

```xml
<yandex>
    <profiles>
        <default>
            <!-- Allow ALTER TABLE ... DROP DETACHED PART[ITION] ... queries. -->
            <allow_drop_detached>1</allow_drop_detached>
        </default>
    </profiles>
</yandex>
```

### Drop the detached parts

```bash
clickhouse-client < drop_detached_parts.sql
```