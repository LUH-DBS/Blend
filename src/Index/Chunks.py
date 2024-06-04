from abc import ABC, abstractmethod
import pandas as pd
from zipfile import ZipFile
import io
import json
import gzip
from pathlib import Path
import urllib.request
from tempfile import TemporaryDirectory

from typing import Iterable, Optional, List

class Chunk(ABC):
    def __init__(self, chunk_label: any):
        self.chunk_label = chunk_label
        self.init_chunk()
    
    @abstractmethod
    def init_chunk(self) -> None:
        pass

    @abstractmethod
    def get_part_labels(self) -> Iterable[any]:
        pass

    @abstractmethod
    def get_part(self, part_label: any) -> pd.DataFrame:
        pass

    def __enter__(self):
        return self

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @classmethod
    @abstractmethod
    def get_chunk_labels(cls) -> Iterable[any]:
        pass

class GitChunk(Chunk):
    def __init__(self, chunk_label: str, cache_dir: Path=Path("/home/schnell/data/gittables")):
        self.cache_dir = cache_dir
        self.parts = None
        self.start = None
        super().__init__(chunk_label)


    def init_chunk(self) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        zip_path = (self.cache_dir / self.chunk_label).with_suffix(".zip")
        if not zip_path.exists():
            urllib.request.urlretrieve(
                "https://zenodo.org/record/6517052/files/" + self.chunk_label + ".zip",
                zip_path)
        self.zf = ZipFile(zip_path)

    def set_start(self, start):
        self.start = start

    def get_part_labels(self) -> List[str]:
        if self.parts is None:
            self.parts = list(sorted(self.zf.namelist()))
        
        return self.parts

    def get_part(self, part_label: str) -> pd.DataFrame:
        if not Path(part_label).suffix != 'parquet':  # optional filtering by filetype
            return None
        try:
            table_name = str(self.get_part_labels().index(part_label) + self.start)
            pq_bytes = self.zf.read(part_label)
            pq_file_like = io.BytesIO(pq_bytes)
            df = pd.read_parquet(pq_file_like, engine="fastparquet")
            df.columns.name = table_name
            return df
        except Exception as e:
            print(f"Error: {part_label=}, {self.chunk_label=} ->", e)
            return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.zf.close()

        

    @classmethod
    def get_chunk_labels(cls) -> List[str]:
        return ["abstraction_tables_licensed", "allegro_con_spirito_tables_licensed", "attrition_rate_tables_licensed", "beats_per_minute_tables_licensed", "beauty_sleep_tables_licensed", "bits_per_second_tables_licensed", "cardiac_output_tables_licensed", "cease_tables_licensed", "centripetal_acceleration_tables_licensed", "channel_capacity_tables_licensed", "clotting_time_tables_licensed", "command_processing_overhead_time_tables_licensed", "count_per_minute_tables_licensed", "crime_rate_tables_licensed", "data_rate_tables_licensed", "dead_air_tables_licensed", "dogwatch_tables_licensed", "dose_rate_tables_licensed", "dwarf_tables_licensed", "entr'acte_tables_licensed", "episcopate_tables_licensed", "erythrocyte_sedimentation_rate_tables_licensed", "escape_velocity_tables_licensed", "fertile_period_tables_licensed", "graveyard_watch_tables_licensed", "growth_rate_tables_licensed", "half_life_tables_licensed", "halftime_tables_licensed", "heterotroph_tables_licensed", "hypervelocity_tables_licensed", "id_tables_licensed", "in_time_tables_licensed", "incubation_period_tables_licensed", "indiction_tables_licensed", "inflation_rate_tables_licensed", "interim_tables_licensed", "kilohertz_tables_licensed", "kilometers_per_hour_tables_licensed", "lapse_tables_licensed", "last_gasp_tables_licensed", "latent_period_tables_licensed", "lead_time_tables_licensed", "living_thing_tables_licensed", "lunitidal_interval_tables_licensed", "meno_mosso_tables_licensed", "menstrual_cycle_tables_licensed", "metabolic_rate_tables_licensed", "miles_per_hour_tables_licensed", "multistage_tables_licensed", "musth_tables_licensed", "neonatal_mortality_tables_licensed", "object_tables_licensed", "orbit_period_tables_licensed", "organism_tables_licensed", "parent_tables_licensed", "peacetime_tables_licensed", "peculiar_velocity_tables_licensed", "physical_entity_tables_licensed", "processing_time_tables_licensed", "question_time_tables_licensed", "quick_time_tables_licensed", "radial_pulse_tables_licensed", "radial_velocity_tables_licensed", "rainy_day_tables_licensed", "rate_of_return_tables_licensed", "reaction_time_tables_licensed", "real_time_tables_licensed", "relaxation_time_tables_licensed", "respiratory_rate_tables_licensed", "return_on_invested_capital_tables_licensed", "revolutions_per_minute_tables_licensed", "rotational_latency_tables_licensed", "running_time_tables_licensed", "safe_period_tables_licensed", "sampling_frequency_tables_licensed", "sampling_rate_tables_licensed", "secretory_phase_tables_licensed", "seek_time_tables_licensed", "shiva_tables_licensed", "show_time_tables_licensed", "solar_constant_tables_licensed", "speed_of_light_tables_licensed", "split_shift_tables_licensed", "steerageway_tables_licensed", "stopping_point_tables_licensed", "terminal_velocity_tables_licensed", "terminus_ad_quem_tables_licensed", "then_tables_licensed", "thing_tables_licensed", "time-out_tables_licensed", "time_interval_tables_licensed", "time_slot_tables_licensed", "track-to-track_seek_time_tables_licensed", "usance_tables_licensed", "wartime_tables_licensed", "whole_tables_licensed"]

class DresdenChunk(Chunk):
    def __init__(self, chunk_label: str, cache_dir: Optional[Path]=Path("/home/schnell/data/dwtc")):
        self.cache_dir = cache_dir
        self.temp_dir = None
        super().__init__(chunk_label)
    
    def set_start(self, start):
        self.start = start

    def init_chunk(self) -> None:
        if self.cache_dir is None:
            self.temp_dir = TemporaryDirectory()
            self.cache_dir = Path(self.temp_dir.name)
        else:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

        gzip_path = (self.cache_dir / f"dwtc-{self.chunk_label:03}").with_suffix(".json.gz")
        if not gzip_path.exists():
            urllib.request.urlretrieve(f"http://wwwdb.inf.tu-dresden.de/misc/dwtc/data_feb15/dwtc-{self.chunk_label:03}.json.gz",
                                       gzip_path)
        self.lines = gzip.open(gzip_path, "rt", encoding="utf-8").readlines()

    def get_part_labels(self) -> Iterable[int]:
        return range(len(self.lines))
    
    def get_part(self, part_label: int) -> pd.DataFrame:
        relation = json.loads(self.lines[part_label])["relation"]
        df = pd.DataFrame(relation)
        n_rows, n_columns = df.shape
        if n_columns > 100:
            return None

        for column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce").fillna(df[column])
        
        df.columns.name = f"{self.start + part_label}"
        return df

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    @classmethod
    def get_chunk_labels(cls) -> Iterable[int]:
        return range(500)
    