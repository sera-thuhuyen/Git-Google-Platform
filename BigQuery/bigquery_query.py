from google.cloud import bigquery
from bigquery_config import get_client, PROJECT_ID
import pandas as pd


# ============================================================
# QUERY
# ============================================================

def run_query(sql: str) -> pd.DataFrame:
    """Chạy câu SQL và trả về DataFrame."""
    client = get_client()
    print(f"⏳ Đang chạy query...")
    df = client.query(sql).to_dataframe()
    print(f"✅ Xong! Trả về {len(df):,} rows")
    return df


def query_table(dataset_id: str, table_id: str, limit: int = 100) -> pd.DataFrame:
    """Lấy dữ liệu từ một bảng, có giới hạn số dòng."""
    sql = f"""
        SELECT *
        FROM `{PROJECT_ID}.{dataset_id}.{table_id}`
        LIMIT {limit}
    """
    return run_query(sql)


# ============================================================
# THAO TÁC VỚI BẢNG
# ============================================================

def list_tables(dataset_id: str) -> list:
    """Liệt kê tất cả bảng trong dataset."""
    client = get_client()
    tables = list(client.list_tables(dataset_id))
    print(f"📋 Các bảng trong dataset '{dataset_id}':")
    for t in tables:
        print(f"   - {t.table_id}")
    return [t.table_id for t in tables]


def get_table_info(dataset_id: str, table_id: str):
    """Xem thông tin chi tiết của một bảng."""
    client = get_client()
    table = client.get_table(f"{PROJECT_ID}.{dataset_id}.{table_id}")
    print(f"📊 Thông tin bảng: {dataset_id}.{table_id}")
    print(f"   Rows   : {table.num_rows:,}")
    print(f"   Created: {table.created}")
    print(f"   Schema :")
    for field in table.schema:
        print(f"      {field.name} ({field.field_type})")
    return table


def delete_table(dataset_id: str, table_id: str):
    """Xóa một bảng."""
    client = get_client()
    table_ref = f"{PROJECT_ID}.{dataset_id}.{table_id}"
    client.delete_table(table_ref, not_found_ok=True)
    print(f"🗑️  Đã xóa bảng: {dataset_id}.{table_id}")


def create_table_from_schema(dataset_id: str, table_id: str, schema: list):
    """
    Tạo bảng mới với schema tùy chỉnh.

    Ví dụ schema:
        schema = [
            bigquery.SchemaField("id", "INTEGER"),
            bigquery.SchemaField("name", "STRING"),
            bigquery.SchemaField("created_at", "TIMESTAMP"),
        ]
    """
    client = get_client()
    table_ref = f"{PROJECT_ID}.{dataset_id}.{table_id}"
    table = bigquery.Table(table_ref, schema=schema)
    table = client.create_table(table, exists_ok=True)
    print(f"✅ Đã tạo bảng: {dataset_id}.{table_id}")
    return table


def insert_rows(dataset_id: str, table_id: str, rows: list):
    """
    Chèn dữ liệu vào bảng (dùng cho số lượng nhỏ).

    Ví dụ rows:
        rows = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]
    """
    client = get_client()
    table_ref = f"{PROJECT_ID}.{dataset_id}.{table_id}"
    errors = client.insert_rows_json(table_ref, rows)
    if errors:
        print(f"❌ Lỗi khi insert: {errors}")
    else:
        print(f"✅ Đã insert {len(rows)} rows vào {dataset_id}.{table_id}")


# ============================================================
# Chạy thử
# ============================================================
if __name__ == "__main__":
    DATASET = "K312"   # Thay dataset ở đây

    # 1. Liệt kê bảng
    # list_tables(DATASET)

    # 2. Xem thông tin bảng
    # get_table_info(DATASET, "address")

    # 3. Query đơn giản
    # df = query_table(DATASET, "ten_bang", limit=10)
    # print(df)

    # 4. Query tùy chỉnh
    df = run_query(f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET}.address`
        ORDER BY 1 ASC
        LIMIT 5
    """)
    print(df)

    # 5. Insert dòng mới
    # insert_rows(DATASET, "ten_bang", [
    #     {"id": 1, "name": "Alice"},
    # ])