# igcse-assessment-tool/src/ingestion.py

import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import shutil

class DataIngestion:
    """Handles loading and merging MCQ, assignment, and participation data."""
    def __init__(self, data_dir: Path):
        data_dir = Path(data_dir)
        if not data_dir.is_dir():
            raise FileNotFoundError(f"No such directory: {data_dir}")
        self.data_dir = data_dir

    def load_mcq_results(self, filename: str = "mcq_results.csv") -> pd.DataFrame:
        path = self.data_dir / filename
        df = pd.read_csv(path)
        # validate 0/1 values
        cols = [c for c in df.columns if c.startswith("q")]
        if df[cols].isin([0, 1]).all().all() is False:
            raise ValueError("MCQ file contains non-binary values")
        return df

    def load_assignments(self, filename: str = "assignments.csv") -> pd.DataFrame:
        path = self.data_dir / filename
        df = pd.read_csv(path)
        return df

    def load_participation(self, filename: str = "participation.csv") -> pd.DataFrame:
        path = self.data_dir / filename
        df = pd.read_csv(path)

        # 找到所有 week_* 列
        week_cols = [c for c in df.columns if c.startswith("week_")]

        # 对每个单独的列做 >=1 和 <=5 的检查，构造布尔掩码
        mask = (df[week_cols] >= 1) & (df[week_cols] <= 5)

        # 如果有任何值不在 1–5 之间，就抛错
        if not mask.all().all():
            raise ValueError("Participation scores outside 1-5 range")

        return df




    def merge_all_data(self) -> "ClassData":
        mcq = self.load_mcq_results()
        assign = self.load_assignments()
        part = self.load_participation()
        # No import needed - StudentRecord and ClassData are already defined above
        cd = ClassData()
        # build StudentRecord per student_id
        for sid in mcq["student_id"]:
            sr = StudentRecord(
                student_id=sid,
                mcq_responses={q: int(r) for q, r in mcq[mcq["student_id"] == sid].iloc[0].items() if q.startswith("q")},
                mcq_total=float(mcq.loc[mcq["student_id"] == sid, "total_score"].iloc[0]),
                assignments=assign[assign["student_id"] == sid].iloc[0].to_dict(),
                assignment_total=float(assign.loc[assign["student_id"] == sid, "total"].iloc[0]),
                participation=part[part["student_id"] == sid].iloc[0].to_dict(),
                participation_avg=float(part.loc[part["student_id"] == sid, "average"].iloc[0]),
            )
            cd.students[sid] = sr
        cd.mcq_questions = [c for c in mcq.columns if c.startswith("q")]
        return cd

class StudentRecord:
    """Represents one student's scores."""
    def __init__(
        self,
        student_id: str,
        mcq_responses: dict,
        mcq_total: float,
        assignments: dict,
        assignment_total: float,
        participation: dict,
        participation_avg: float,
    ):
        if not student_id:
            raise ValueError("Student ID cannot be empty")
        if any(v not in (0, 1) for v in mcq_responses.values()):
            raise ValueError("MCQ response values must be 0 or 1")
        self.student_id = student_id
        self.mcq_responses = mcq_responses
        self.mcq_total = mcq_total
        self.assignments = assignments
        self.assignment_total = assignment_total
        self.participation = participation
        self.participation_avg = participation_avg

class ClassData:
    """Holds an entire class’s worth of StudentRecords."""
    def __init__(self):
        self.students = {}
        self.mcq_questions = []

    @property
    def num_students(self) -> int:
        return len(self.students)

    @property
    def num_questions(self) -> int:
        return len(self.mcq_questions)

def generate_sample_data(
    output_dir: Path,
    num_students: int = 10,
    num_questions: int = 5,
) -> None:
    """
    Create sample_mcq_results.csv, sample_assignments.csv,
    sample_participation.csv in output_dir.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    # MCQ
    mcq = pd.DataFrame({
        "student_id": [f"S{i+1:03d}" for i in range(num_students)],
        **{f"q{j+1}": np.random.randint(0, 2, num_students) for j in range(num_questions)},
        "total_score": np.random.randint(0, num_questions + 1, num_students),
    })
    mcq.to_csv(output_dir / "sample_mcq_results.csv", index=False)

    # Assignments
    assign = pd.DataFrame({
        "student_id": mcq["student_id"],
        **{f"assignment_{k+1}": np.random.uniform(60, 100, num_students) for k in range(3)},
        "total": np.random.uniform(180, 300, num_students),
    })
    assign.to_csv(output_dir / "sample_assignments.csv", index=False)

    # Participation
    part = pd.DataFrame({
        "student_id": mcq["student_id"],
        **{f"week_{w+1}": np.random.randint(1, 6, num_students) for w in range(4)},
        "average": np.random.uniform(1, 5, num_students),
    })
    part.to_csv(output_dir / "sample_participation.csv", index=False)
if __name__ == "__main__":
    # Quick test
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Generate sample data
        generate_sample_data(Path(tmpdir), num_students=5, num_questions=10)
        
        # Test loading
        ingestion = DataIngestion(Path(tmpdir))
        
        # Rename files to match expected names
        (Path(tmpdir) / 'sample_mcq_results.csv').rename(
            Path(tmpdir) / 'mcq_results.csv'
        )
        (Path(tmpdir) / 'sample_assignments.csv').rename(
            Path(tmpdir) / 'assignments.csv'
        )
        (Path(tmpdir) / 'sample_participation.csv').rename(
            Path(tmpdir) / 'participation.csv'
        )
        
        class_data = ingestion.merge_all_data()
        
        print(f"✅ Successfully loaded {class_data.num_students} students")
        print(f"📊 MCQ questions: {class_data.num_questions}")
        print(f"📚 Number of students: {class_data.num_students}")
        
        # Show sample student
        if class_data.students:
            sample_student = list(class_data.students.values())[0]
            print(f"\n👤 Sample student: {sample_student.student_id}")
            print(f"   - MCQ score: {sample_student.mcq_total}")
            print(f"   - Assignment total: {sample_student.assignment_total:.1f}")
            print(f"   - Participation avg: {sample_student.participation_avg:.1f}")