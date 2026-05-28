from google.cloud import bigquery
from google.oauth2 import service_account
import os

# ============================================================
# CẤU HÌNH - chỉnh sửa các giá trị này
# ============================================================
SERVICE_ACCOUNT_FILE = "project-thuhuyen-2023-bigquery.json"
PROJECT_ID = "project-thuhuyen-2023"

BASE_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
# ============================================================


def get_client() -> bigquery.Client:
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


def get_data_path(filename: str, subfolder: str = "") -> str:
    """
    Trả về đường dẫn đầy đủ tới file CSV.
    Cấu trúc: data/{subfolder}/{filename}

    Args:
        filename  : Tên file CSV (ví dụ: "sales.csv")
        subfolder : Tên folder con trong data/ (ví dụ: "K312")
    """
    folder = os.path.join(BASE_DATA_DIR, subfolder) if subfolder else BASE_DATA_DIR
    path = os.path.join(folder, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Không tìm thấy file: {path}\n"
            f"Hãy đặt file CSV vào thư mục: {folder}"
        )
    return path


# Test kết nối
if __name__ == "__main__":
    try:
        os.makedirs(BASE_DATA_DIR, exist_ok=True)

        client = get_client()
        print(f"✅ Kết nối thành công!")
        print(f"   Project : {client.project}")
        print(f"   Data dir: {BASE_DATA_DIR}")

        datasets = list(client.list_datasets())
        print(f"   Datasets ({len(datasets)}):")
        for ds in datasets:
            print(f"   - {ds.dataset_id}")
    except Exception as e:
        print(f"❌ Lỗi kết nối: {e}")