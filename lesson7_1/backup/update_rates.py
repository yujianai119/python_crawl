"""Simplified standalone updater for exchange rates."""

import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from rates.crawler import fetch_rates, fetch_usd_rates_all_banks
from rates.normalize import normalize_rates
from rates.storage import write_cache


class UpdateService:
    """Handles rate update operations with logging."""
    
    def __init__(self, log_path: Optional[Path] = None):
        self.log_path = log_path or Path(__file__).parent / "rates" / "data" / "update.log"
        self._ensure_log_dir()
    
    def _ensure_log_dir(self):
        """Ensure log directory exists."""
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def log(self, message: str):
        """Write timestamped log entry."""
        timestamp = datetime.now(timezone.utc).isoformat()
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    
    def update_rates(self) -> bool:
        """Update rates and return success status."""
        try:
            self.log("開始更新匯率")
            
            # Fetch and process data
            raw_data = fetch_rates()
            all_banks_usd = fetch_usd_rates_all_banks()
            self.log(f"成功抓取 {len(raw_data or [])} 筆資料")
            
            normalized_data = normalize_rates(raw_data)
            write_cache(normalized_data, all_banks_usd)
            
            self.log("更新完成")
            print("更新完成")
            return True
            
        except Exception as e:
            error_msg = f"更新失敗: {str(e)}"
            self.log(error_msg)
            self.log(traceback.format_exc())
            print(f"更新失敗，詳見日誌: {self.log_path}")
            return False


def main():
    """Main entry point."""
    service = UpdateService()
    success = service.update_rates()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
