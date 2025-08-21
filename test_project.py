from project import get_files, get_data, format_name


def test_get_files():
    assert get_files("data/transcripts")[0].name.endswith(".pdf")
    assert get_files("data/empty") == []


def test_get_data():
    assert get_data("""BẢNG ĐIỂM \n Họ tên (Full Name): Student A \n Mã số sinh viên (Student ID): 2410001""") == "2410001"
    assert get_data("""Họ tên (Full Name): Student B \n Mã số sinh viên (Student ID): 2410002   """) == "2410002"


def test_format_name():
    assert format_name({"name": "Student A", "id": "2410001"}) == "2410001_Bảng điểm_Student A.pdf"
    assert format_name({"name": "Student B", "id": "2410002"}) == "2410002_Bảng điểm_Student B.pdf"
