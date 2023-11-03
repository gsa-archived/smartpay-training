from typing import List
import pytest
from training import models, schemas
from training.repositories import UserRepository, AgencyRepository


def test_create(user_repo_empty: UserRepository, agency_repo_with_data: AgencyRepository):
    agency_id = agency_repo_with_data.find_all()[0].id
    new_user = schemas.UserCreate(
        email="new_user@example.com",  # type: ignore
        name="New User",
        agency_id=agency_id
    )
    db_user = user_repo_empty.create(new_user)
    assert db_user.id
    assert db_user.name == "New User"


def test_create_duplicate(user_repo_with_data: UserRepository):
    existing_user = user_repo_with_data.find_all()[0]
    duplicate_user = schemas.UserCreate(
        email=existing_user.email,  # type: ignore
        name="Duplicate User",
        agency_id=existing_user.agency_id
    )
    with pytest.raises(Exception):
        user_repo_with_data.create(duplicate_user)


def test_find_by_email(user_repo_with_data: UserRepository, valid_user_dict):
    result = user_repo_with_data.find_by_email(valid_user_dict["email"])
    assert result is not None
    assert result.name == valid_user_dict["name"]


def test_find_by_nonexistent_email(user_repo_empty: UserRepository):
    result = user_repo_empty.find_by_email("nonexistent.email@example.com")
    assert result is None


def test_save(user_repo_empty: UserRepository, agency_repo_with_data: AgencyRepository):
    agency_id = agency_repo_with_data.find_all()[0].id
    result = user_repo_empty.save(models.User(
        email="newuser@example.com",
        name="New User",
        agency_id=agency_id,
    ))
    assert result.id
    retrieved_result = user_repo_empty.find_by_id(result.id)
    assert retrieved_result is not None
    assert retrieved_result.name == "New User"


def test_find_by_id(user_repo_with_data: UserRepository, valid_user_ids: List[int]):
    result = user_repo_with_data.find_by_id(valid_user_ids[0])
    assert result is not None
    assert result.id == valid_user_ids[0]


def test_find_by_nonexistent_id(user_repo_with_data: UserRepository, valid_user_ids):
    nonexistent_user_id = 0
    while nonexistent_user_id in valid_user_ids:
        nonexistent_user_id += 1
    result = user_repo_with_data.find_by_id(nonexistent_user_id)
    assert result is None


def test_find_all(user_repo_with_data: UserRepository, testdata: dict):
    result = user_repo_with_data.find_all()
    emails = list(map(lambda r: r.email, result))
    for valid_user in testdata["users"]:
        assert valid_user["email"] in emails


def test_delete_by_id(user_repo_with_data: UserRepository, valid_user_ids: List[int]):
    db_user = user_repo_with_data.find_by_id(valid_user_ids[0])
    db_user.roles = []
    db_user.report_agencies = []
    user_repo_with_data._session.commit()
    user_repo_with_data.delete_by_id(valid_user_ids[0])
    assert user_repo_with_data.find_by_id(valid_user_ids[0]) is None


def test_edit_user_for_reporting(user_repo_with_data: UserRepository, valid_user_ids: List[int]):
    valid_user_id = valid_user_ids[0]
    valid_agency = user_repo_with_data._session.query(models.Agency).first()
    valid_agency_list = [valid_agency.id]
    result = user_repo_with_data.edit_user_for_reporting(valid_user_id, valid_agency_list)
    assert result is not None
    assert result.roles is not None and any(role.name == "Report" for role in result.roles)
    assert result.report_agencies is not None and any(agency.id == valid_agency.id for agency in result.report_agencies)


def test_invalid_edit_user_for_reporting(user_repo_with_data: UserRepository):
    invalid_user_id = 0
    invalid_agency_id_list = [0]

    with pytest.raises(Exception):
        user_repo_with_data.create(invalid_user_id, invalid_agency_id_list)


def test_get_users(user_repo_with_data: UserRepository, valid_user_ids: List[int]):
    valid_user_id = valid_user_ids[0]
    db_user = user_repo_with_data.find_by_id(valid_user_id)
    search_criteria = db_user.name[:-1]
    result = user_repo_with_data.get_users(search_criteria, 1)
    assert result is not None
    for item in result.users:
        assert search_criteria in item.name


def test_get_users_by_email(user_repo_with_data: UserRepository, valid_user_ids: List[int]):
    valid_user_id = valid_user_ids[0]
    db_user = user_repo_with_data.find_by_id(valid_user_id)
    search_criteria = db_user.email[:-1]
    result = user_repo_with_data.get_users(search_criteria, 1)
    assert result is not None
    for item in result.users:
        assert search_criteria in item.email
