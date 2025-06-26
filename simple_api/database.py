"""Mocked database implementation using multiprocessing for thread safety."""

import multiprocessing
from datetime import datetime
from typing import Any, Dict, List

from simple_api.models import VisitRequest


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
        self.visits = self.manager.list()

        # Shared integer to track total visit count
        self.visit_count = self.manager.Value("i", 0)  # 'i' for integer

        # Lock for thread-safe operations
        self.lock = self.manager.Lock()

    def add_page_visit(self, visit_data: VisitRequest) -> int:
        """
        Add a page visit to the database with thread-safe operations.

        Args:
            visit_data: VisitRequest object containing visit information

        Returns:
            int: Updated total visit count
        """
        with self.lock:
            # Create visit record with timestamp
            visit_record = {
                "user_id": visit_data.user_id,
                "page_url": visit_data.page_url,
                "user_agent": visit_data.user_agent,
                "ip_address": visit_data.ip_address,
                "referrer": visit_data.referrer,
                "timestamp": datetime.now().isoformat(),
            }

            # Add to visits list
            self.visits.append(visit_record)

            # Increment visit count
            self.visit_count.value += 1

            return self.visit_count.value

    def get_total_visits(self) -> int:
        """Get the total number of visits."""
        return self.visit_count.value

    def get_recent_visits(self, hours: float = 1.0) -> int:
        """
        Get the number of visits within the specified number of hours.

        Args:
            hours: Number of hours to look back (default: 1.0)

        Returns:
            int: Number of recent visits
        """
        with self.lock:
            current_time = datetime.now()
            recent_count = 0

            for visit in self.visits:
                visit_time = datetime.fromisoformat(visit["timestamp"])
                time_diff = current_time - visit_time

                if time_diff.total_seconds() <= (hours * 3600):
                    recent_count += 1

            return recent_count

    def get_all_visits(self) -> List[Dict[str, Any]]:
        """Get all visit records (for debugging purposes)."""
        with self.lock:
            return list(self.visits)
