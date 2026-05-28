from google.cloud import bigquery
from google.oauth2 import service_account
import os

# ============================================================
# CẤU HÌNH - chỉnh sửa các giá trị này
# ============================================================
SERVICE_ACCOUNT_FILE = "project-thuhuyen-2023-bigquery.json"  # Đường dẫn tới file JSON
PROJECT_ID = "project-thuhuyen-2023"       # Google Cloud Project ID

# Thư mục chứa file CSV (luôn cố định)
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
# ============================================================


def get_client(dataset_id: str = None) -> bigquery.Client:
    """Tạo và trả về BigQuery client đã xác thực."""
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        raise FileNotFoundError(
            f"Không tìm thấy file service account: {SERVICE_ACCOUNT_FILE}"
        )

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )

    client = bigquery.Client(
        credentials=credentials,
        project=PROJECT_ID,
    )
    return client


def get_table_ref(client: bigquery.Client, dataset_id: str, table_id: str) -> bigquery.TableReference:
    """Trả về reference tới một bảng cụ thể."""
    return client.dataset(dataset_id).table(table_id)


def get_data_path(filename: str) -> str:
    """
    Trả về đường dẫn đầy đủ tới file CSV trong thư mục data/.

    Ví dụ: get_data_path("sales.csv") -> "/your/project/data/sales.csv"
    """
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Không tìm thấy file: {path}\n"
            f"Hãy đặt file CSV vào thư mục: {DATA_DIR}"
        )
    return path


# Test kết nối
if __name__ == "__main__":
    try:
        # Tạo thư mục data nếu chưa có
        os.makedirs(DATA_DIR, exist_ok=True)

        client = get_client()
        print(f"✅ Kết nối thành công!")
        print(f"   Project : {client.project}")
        print(f"   Data dir: {DATA_DIR}")

        # List các dataset
        datasets = list(client.list_datasets())
        print(f"   Datasets ({len(datasets)}):")
        for ds in datasets:
            print(f"   - {ds.dataset_id}")
    except Exception as e:
        print(f"❌ Lỗi kết nối: {e}")
