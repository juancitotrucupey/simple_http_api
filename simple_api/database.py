"""Mocked database implementation using multiprocessing for thread safety."""

import multiprocessing
from datetime import datetime
from typing import Any, Dict, List

from simple_api.models import BuyInformation


class MockedDB:
    """
    Mocked database using multiprocessing shared objects to simulate external database.

    Uses multiprocessing.Manager to create shared objects that can be safely accessed
    across multiple processes/threads with proper locking mechanisms.
    """

    def __init__(self):
        """Initialize the mocked database with shared objects."""
        self.manager = multiprocessing.Manager()

        # Shared list to store visit records
        self.buys = self.manager.list()

        # Shared integer to track total visit count
        self.buy_count = self.manager.Value("i", 0)  # 'i' for integer

        # Lock for thread-safe operations
        self.lock = self.manager.Lock()

    def add_product_buy(self, buy_data: BuyInformation) -> int:
        """
        Add a product buy to the database with thread-safe operations.

        Args:
            buy_data: BuyInformation object containing buy information

        Returns:
            int: Updated total buy count
        """
        with self.lock:
            # Create visit record with timestamp
            buy_record = {
                "user_id": buy_data.user_id,
                "promotion_id": buy_data.promotion_id,
                "product_id": buy_data.product_id,
                "product_quantity": buy_data.product_quantity,
                "ip_address": buy_data.ip_address,
                "timestamp": buy_data.timestamp.isoformat(),
            }

            # Add to buys list
            self.buys.append(buy_record)

            # Increment visit count
            self.buy_count.value += buy_data.product_quantity

            return self.buy_count.value

    def get_total_buys(self) -> int:
        """Get the total number of buys."""
        return self.buy_count.value

    def get_recent_buys(self, hours: float = 1.0) -> int:
        """
        Get the number of buys within the specified number of hours.

        Args:
            hours: Number of hours to look back (default: 1.0)

        Returns:
            int: Number of recent visits
        """
        with self.lock:
            current_time = datetime.now()
            recent_count = 0

            for buy in self.buys:
                buy_time = datetime.fromisoformat(buy["timestamp"])
                time_diff = current_time - buy_time

                if time_diff.total_seconds() <= (hours * 3600):
                    recent_count += 1

            return recent_count

    def get_all_buys(self) -> List[Dict[str, Any]]:
        """Get all buy records (for debugging purposes)."""
        with self.lock:
            return list(self.buys)
