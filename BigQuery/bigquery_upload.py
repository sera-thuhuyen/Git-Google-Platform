from google.cloud import bigquery
from bigquery_config import get_client, get_table_ref, get_data_path, PROJECT_ID, BASE_DATA_DIR
import os


def create_dataset_if_not_exists(client: bigquery.Client, dataset_id: str, location: str = "US"):
    """Tạo dataset nếu chưa tồn tại."""
    dataset_ref = f"{PROJECT_ID}.{dataset_id}"
    try:
        client.get_dataset(dataset_ref)
        print(f"   Dataset '{dataset_id}' đã tồn tại")
    except Exception:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = location
        client.create_dataset(dataset)
        print(f"   Đã tạo dataset mới: '{dataset_id}'")


def upload_csv(
    filename: str,
    dataset_id: str,
    subfolder: str = "",
    write_mode: str = "WRITE_TRUNCATE",
    skip_rows: int = 1,
    autodetect: bool = True,
    schema: list = None,
    location: str = "US",
):
    """
    Upload file CSV từ thư mục data/ lên BigQuery.
    Tên bảng tự động lấy từ tên file (bỏ đuôi .csv).

    Args:
        filename   : Tên file CSV trong thư mục data/ (ví dụ: "sales.csv")
        dataset_id : Dataset đích trong BigQuery (tự tạo nếu chưa có)
        write_mode : Cách ghi dữ liệu:
                       "WRITE_TRUNCATE" - Xóa bảng cũ và ghi mới (mặc định)
                       "WRITE_APPEND"   - Thêm vào bảng hiện có
                       "WRITE_EMPTY"    - Chỉ ghi nếu bảng đang trống
        skip_rows  : Số dòng đầu bỏ qua (1 = bỏ header)
        autodetect : Tự động nhận diện schema từ CSV
        schema     : Schema tùy chỉnh (nếu autodetect=False)
        location   : Region của dataset (mặc định "US")
    """
    # Tên bảng = tên file bỏ đuôi .csv
    table_id = os.path.splitext(filename)[0]
    csv_file_path = get_data_path(filename, subfolder)

    client = get_client()

    # Tự tạo dataset nếu chưa có
    create_dataset_if_not_exists(client, dataset_id, location)

    table_ref = get_table_ref(client, dataset_id, table_id)

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=skip_rows,
        autodetect=autodetect,
        write_disposition=write_mode,
        schema=schema,
    )

    print(f"⏳ Đang upload '{filename}' lên {dataset_id}.{table_id}...")

    with open(csv_file_path, "rb") as f:
        job = client.load_table_from_file(f, table_ref, job_config=job_config)

    job.result()  # Chờ job hoàn tất

    table = client.get_table(table_ref)
    print(f"✅ Upload thành công!")
    print(f"   Bảng  : {PROJECT_ID}.{dataset_id}.{table_id}")
    print(f"   Rows  : {table.num_rows:,}")
    print(f"   Schema: {[f.name for f in table.schema]}")


def upload_all_csv(dataset_id: str, write_mode: str = "WRITE_TRUNCATE", location: str = "US"):
    """
    Upload tất cả file CSV trong thư mục data/ lên cùng 1 dataset.
    Mỗi file sẽ tạo thành 1 bảng riêng, tên bảng = tên file bỏ .csv.
    """
    files = list_csv_files()
    if not files:
        print("⚠️  Không có file CSV nào trong thư mục data/")
        return

    print(f"\n⏳ Bắt đầu upload {len(files)} file lên dataset '{dataset_id}'...\n")
    for filename in files:
        upload_csv(filename, dataset_id, write_mode=write_mode, location=location)
        print()
    print(f"🎉 Hoàn tất! Đã upload {len(files)} file.")


def upload_csv_from_dataframe(df, dataset_id: str, table_id: str, write_mode: str = "WRITE_TRUNCATE", location: str = "US"):
    """
    Upload DataFrame lên BigQuery (không cần lưu ra file CSV).

    Args:
        df         : pandas DataFrame
        dataset_id : Dataset đích (tự tạo nếu chưa có)
        table_id   : Tên bảng đích
        write_mode : Cách ghi dữ liệu
        location   : Region của dataset
    """
    client = get_client()
    create_dataset_if_not_exists(client, dataset_id, location)
    table_ref = get_table_ref(client, dataset_id, table_id)

    job_config = bigquery.LoadJobConfig(
        write_disposition=write_mode,
        autodetect=True,
    )

    print(f"⏳ Đang upload DataFrame lên {dataset_id}.{table_id}...")
    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    job.result()

    table = client.get_table(table_ref)
    print(f"✅ Upload thành công! Rows: {table.num_rows:,}")


def list_csv_files(subfolder: str = "") -> list:
    folder = os.path.join(BASE_DATA_DIR, subfolder) if subfolder else BASE_DATA_DIR
    if not os.path.exists(folder):
        print(f"⚠️  Thư mục chưa tồn tại: {folder}")
        return []
    files = [f for f in os.listdir(folder) if f.endswith(".csv")]
    print(f"📁 File CSV trong '{folder}':")
    for f in files:
        size = os.path.getsize(os.path.join(folder, f)) / 1024
        # print(f"   - {f} ({size:.1f} KB)  →  bảng: {os.path.splitext(f)[0]}")
    return files

def upload_file (dataset_id: str, files_list: list, subfolder: str = ""):
    for filename in files_list:
        upload_csv(filename=filename, dataset_id=dataset_id, subfolder=subfolder)

# ============================================================
# Chạy thử
# ============================================================
if __name__ == "__main__":
    DATASET = "K312"   

    # Danh sách file muốn upload
    files_to_upload = [
        "address.csv"
    ]

    subfolder = "film_folder"  # Nếu file nằm trong data/K312/ thì đặt tên subfolder là "K312", nếu nằm trực tiếp trong data/ thì để subfolder = ""

    upload_file(DATASET, files_to_upload, subfolder)