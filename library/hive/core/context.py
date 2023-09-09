import abc
import dataclasses
import datetime
import os
from typing import Any

from loguru import logger


@dataclasses.dataclass
class HiveContext:
    database: str
    date: datetime.date | None = None
    start_date: datetime.date | None = None
    end_date: datetime.date | None = None
    extra_partition_params: dict[str, Any] | None = None

    def __post_init__(self):
        if os.getenv("HIVE_TEST_DATABASE"):
            logger.info(
                f"HIVE_TEST_DATABASE is set. Using test database. {self.database} is ignored."
            )
            self.database = os.getenv("HIVE_TEST_DATABASE")

        self._run_validation()

    @property
    def is_period(self) -> bool:
        return bool(self.start_date and self.end_date)

    def _run_validation(self):
        if bool(self.start_date) ^ bool(self.end_date):
            raise ValueError(
                "Cannot enter only one of the two values(start_date and end_date)."
            )

        if self.date and self.start_date and self.end_date:
            raise ValueError("Context type cannot be both date and period.")


class HiveContextMixin:
    _ctx = None

    def add_ctx(
        self,
        database: str,
        date: datetime.date | None = None,
        start_date: datetime.date | None = None,
        end_date: datetime.date | None = None,
        **kwargs,
    ):
        self._ctx = HiveContext(
            database=database,
            date=date,
            start_date=start_date,
            end_date=end_date,
            extra_partition_params=kwargs,
        )
        return self

    @property
    def database(self):
        return self._ctx.database


class HivePartitionContextMixin(HiveContextMixin, abc.ABC):
    @property
    @abc.abstractmethod
    def partition_params(self) -> dict[str, Any]:
        pass


class HiveDatePartitionContextMixin(HivePartitionContextMixin):
    """HiveContextMixin with date partitioned table

    HiveContext could have one of two attributes: Date or Period.
    If the attribute is date, date property will only be used.
    Else, period property (start_date, end_date) will only be used.
    It is not possible to use both date and period property at once.
    """

    _flat_partition: bool

    @property
    def date(self) -> datetime.date:
        return self._ctx.date

    @property
    def start_date(self) -> datetime.date:
        return self._ctx.start_date

    @property
    def end_date(self) -> datetime.date:
        return self._ctx.end_date

    @property
    def has_multi_partition(self) -> bool:
        return self._ctx.is_period

    @property
    def partition_params(self) -> dict[str, Any]:
        if self._flat_partition:
            return {"date": self.date}
        return {
            "year": self.date.year if self.date else -1,
            "month": self.date.month if self.date else -1,
            "day": self.date.day if self.date else -1,
        }


class HiveDatePartitionWithExtraContextMixin(HiveDatePartitionContextMixin):
    @property
    def partition_params(self) -> dict[str, Any]:
        partition_params = super().partition_params
        partition_params.update(self._ctx.extra_partition_params)
        return partition_params

    @property
    def has_multi_partition(self) -> bool:
        if super().has_multi_partition:
            return True

        return not all(v for v in self._ctx.extra_partition_params.values())
