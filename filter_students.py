import argparse
import csv
from pathlib import Path


DEFAULT_STUDENTS = "student_list_proc1008.csv"
DEFAULT_GRADES = "gc_PROC1008_2026_SPR_columns_2026-08-18-14-57-41.csv"
DEFAULT_OUTPUT = "gc_PROC1008_2026_SPR_columns_filtered.csv"


def read_student_codes(path: Path) -> set[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        student_code_column = next(
            (
                name
                for name in reader.fieldnames or []
                if name.strip().casefold() == "student_code"
            ),
            None,
        )
        if student_code_column is None:
            raise ValueError(f"{path} does not contain a STUDENT_CODE column")

        return {
            row[student_code_column].strip().casefold()
            for row in reader
            if row.get(student_code_column, "").strip()
        }


def filter_grades(student_codes: set[str], input_path: Path, output_path: Path) -> tuple[int, int]:
    with input_path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        if not reader.fieldnames or "Student ID" not in reader.fieldnames:
            raise ValueError(f"{input_path} does not contain a Student ID column")

        with output_path.open("w", encoding="utf-8-sig", newline="") as destination:
            writer = csv.DictWriter(destination, fieldnames=reader.fieldnames)
            writer.writeheader()

            kept = 0
            removed = 0
            for row in reader:
                if row.get("Student ID", "").strip().casefold() in student_codes:
                    writer.writerow(row)
                    kept += 1
                else:
                    removed += 1

    return kept, removed


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Keep only grade-center rows whose Student ID appears as a STUDENT_CODE."
    )
    parser.add_argument("students", nargs="?", default=DEFAULT_STUDENTS, type=Path)
    parser.add_argument("grades", nargs="?", default=DEFAULT_GRADES, type=Path)
    parser.add_argument("output", nargs="?", default=DEFAULT_OUTPUT, type=Path)
    args = parser.parse_args()

    student_codes = read_student_codes(args.students)
    kept, removed = filter_grades(student_codes, args.grades, args.output)
    print(f"Wrote {args.output}: kept {kept} rows and removed {removed} rows.")


if __name__ == "__main__":
    main()
