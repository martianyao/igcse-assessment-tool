# igcse-assessment-tool/tests/test_ingestion.py

import pytest
import pandas as pd
from pathlib import Path
import tempfile
import shutil

from src.ingestion import (
    DataIngestion,
    StudentRecord,
    ClassData,
    generate_sample_data,
)

class TestStudentRecord:
    def test_valid_and_invalid(self):
        rec = StudentRecord(
            student_id="S001",
            mcq_responses={"q1": 1},
            mcq_total=1.0,
            assignments={},
            assignment_total=0.0,
            participation={},
            participation_avg=0.0,
        )
        assert rec.student_id == "S001"
        with pytest.raises(ValueError):
            StudentRecord(
                student_id="",
                mcq_responses={"q1": 0},
                mcq_total=0.0,
                assignments={},
                assignment_total=0.0,
                participation={},
                participation_avg=0.0,
            )
        with pytest.raises(ValueError):
            StudentRecord(
                student_id="S002",
                mcq_responses={"q1": 2},
                mcq_total=0.0,
                assignments={},
                assignment_total=0.0,
                participation={},
                participation_avg=0.0,
            )

class TestClassData:
    def test_empty(self):
        cd = ClassData()
        assert cd.num_students == 0
        assert cd.num_questions == 0

class TestDataIngestion:
    def setup_method(self):
        self.tmp = tempfile.mkdtemp()
        self.path = Path(self.tmp)
    def teardown_method(self):
        shutil.rmtree(self.tmp)

    def test_mcq_flow(self):
        df = pd.DataFrame({"student_id": ["S1"], "q1": [1], "total_score": [1]})
        df.to_csv(self.path / "mcq_results.csv", index=False)
        di = DataIngestion(self.path)
        out = di.load_mcq_results()
        assert "q1" in out.columns

    def test_participation_error(self):
        pd.DataFrame({"student_id": ["S1"], "week_1": [6], "average": [6]}).to_csv(
            self.path / "participation.csv", index=False
        )
        di = DataIngestion(self.path)
        with pytest.raises(ValueError):
            di.load_participation()

class TestGenerateSampleData:
    def test_creates_files(self, tmp_path):
        generate_sample_data(tmp_path, num_students=2, num_questions=2)
        assert (tmp_path / "sample_mcq_results.csv").exists()
        assert (tmp_path / "sample_assignments.csv").exists()
        assert (tmp_path / "sample_participation.csv").exists()
