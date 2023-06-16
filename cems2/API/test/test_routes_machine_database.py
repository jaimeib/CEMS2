"""Integration test for API with system database."""

import json

import pytest
from fastapi import status as HTTPStatus
from fastapi.testclient import TestClient

from cems2.API.api import api


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(api)


# Test GET "/machines/" route with machines in the database
def test_get_machines(client):
    """Test GET "/machines/" route with machines in the database."""
    response = client.get("/machines/")
    assert response.status_code == HTTPStatus.HTTP_200_OK


# Test GET "/machines/" route with a filter of a groupname that exists
@pytest.mark.parametrize("groupname", ["cloudA", "cloudB", "cloudC", "cloudD"])
def test_get_machines_filter_groupname(client, groupname):
    """Test GET "/machines/" route with a filter of a groupname that exists."""
    response = client.get(f"/machines?group_name={groupname}")
    assert response.status_code == HTTPStatus.HTTP_200_OK


# Test GET "/machines/" route with a filter of a groupname that does not exist
@pytest.mark.parametrize("groupname", ["cloudE", "cloudF", "cloudG", "cloudH"])
def test_get_machines_filter_groupname_not_exist(client, groupname):
    """Test GET "/machines/" route with a filter of a groupname that does not exist."""
    response = client.get(f"/machines?group_name={groupname}")
    assert response.status_code == HTTPStatus.HTTP_200_OK


# Test GET "/machines/" route with a filter of a brand that exists
@pytest.mark.parametrize("brand", ["IBM Power 8", "Lenovo", "Dell", "HP"])
def test_get_machines_filter_brand(client, brand):
    """Test GET "/machines/" route with a filter of a brand that exists."""
    response = client.get(f"/machines?brand={brand}")
    assert response.status_code == HTTPStatus.HTTP_200_OK


# Test GET "/machines/" route with a filter of a brand that does not exist
@pytest.mark.parametrize(
    "brand", ["IBM Power 9", "IMB Power 10", "IBM Power 11", "IBM Power 12"]
)
def test_get_machines_filter_brand_not_exist(client, brand):
    """Test GET "/machines/" route with a filter of a brand that does not exist."""
    response = client.get(f"/machines?brand_model={brand}")
    assert response.status_code == HTTPStatus.HTTP_200_OK


# Test GET "/machines/" route with a filter of a connector that exists
@pytest.mark.parametrize("connector", ["test", "test2"])
def test_get_machines_filter_connection(client, connector):
    """Test GET "/machines/" route with a filter of a connector that exists."""
    response = client.get(f"/machines?connector={connector}")
    assert response.status_code == HTTPStatus.HTTP_200_OK


# Test GET "/machines/" route with a filter of a connector that does not exist
@pytest.mark.parametrize("connector", ["test3", "test4"])
def test_get_machines_filter_connection_not_exist(client, connector):
    """Test GET "/machines/" route with a filter of a connector that does not exist."""
    response = client.get(f"/machines?connector={connector}")
    assert response.status_code == HTTPStatus.HTTP_200_OK


# Test GET "/machines/" route with a filter of energy_status = ON
def test_get_machines_filter_energy_status_on(client):
    """Test GET "/machines/" route with a filter of energy_status = True."""
    response = client.get("/machines?energy_status=True")
    assert response.status_code == HTTPStatus.HTTP_200_OK


# Test GET "/machines/" route with a filter of energy_status = OFF
def test_get_machines_filter_energy_status_off(client):
    """Test GET "/machines/" route with a filter of energy_status = False."""
    response = client.get("/machines?energy_status=False")
    assert response.status_code == HTTPStatus.HTTP_200_OK


# Test GET "/machines/" route with a filter of energy_status = Other value
def test_get_machines_filter_energy_status_other(client):
    """Test GET "/machines/" route with a filter of energy_status = Other value."""
    response = client.get("/machines?energy_status=Other")
    assert response.status_code == HTTPStatus.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json() == {
        "detail": [
            {
                "loc": ["query", "energy_status"],
                "msg": "value could not be parsed to a boolean",
                "type": "type_error.bool",
            }
        ]
    }


# Test GET "/machines/" route with a filter of monitoring = ON
def test_get_machines_filter_monitoring_on(client):
    """Test GET "/machines/" route with a filter of monitoring = True."""
    response = client.get("/machines?monitoring=True")
    assert response.status_code == HTTPStatus.HTTP_200_OK
    assert response.json() == []  # No machines are being monitored in a initial state


# Test GET "/machines/" route with a filter of monitoring = OFF
def test_get_machines_filter_monitoring_off(client):
    """Test GET "/machines/" route with a filter of monitoring = False."""
    response = client.get("/machines?monitoring=False")
    assert response.status_code == HTTPStatus.HTTP_200_OK
    assert response.json() != []
    for machine in response.json():
        assert machine["monitoring"] == False


# Test GET "/machines/" route with a filter of monitoring = Other value
def test_get_machines_filter_monitoring_other(client):
    """Test GET "/machines/" route with a filter of monitoring = Other value."""
    response = client.get("/machines?monitoring=Other")
    assert response.status_code == HTTPStatus.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json() == {
        "detail": [
            {
                "loc": ["query", "monitoring"],
                "msg": "value could not be parsed to a boolean",
                "type": "type_error.bool",
            }
        ]
    }


# Test GET "/machines/" route with a filter of available = ON
def test_get_machines_filter_available_on(client):
    """Test GET "/machines/" route with a filter of available = True."""
    response = client.get("/machines?available=True")
    assert response.status_code == HTTPStatus.HTTP_200_OK


# Test GET "/machines/" route with a filter of available = OFF
def test_get_machines_filter_available_off(client):
    """Test GET "/machines/" route with a filter of available = False."""
    response = client.get("/machines?available=False")
    assert response.status_code == HTTPStatus.HTTP_200_OK


# Test GET "/machines/" route with a filter of available = Other value
def test_get_machines_filter_available_other(client):
    """Test GET "/machines/" route with a filter of available = Other value."""
    response = client.get("/machines?available=Other")
    assert response.status_code == HTTPStatus.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json() == {
        "detail": [
            {
                "loc": ["query", "available"],
                "msg": "value could not be parsed to a boolean",
                "type": "type_error.bool",
            }
        ]
    }


# Test GET "/machines/" route with multiple valid filters
@pytest.mark.parametrize("groupname", ["cloudA", "cloudB", "cloudC", "cloudD"])
@pytest.mark.parametrize("brand", ["IBM Power 8", "Lenovo", "Dell", "HP"])
@pytest.mark.parametrize("connector", ["test", "test2"])
@pytest.mark.parametrize("energy_status", ["True", "False"])
@pytest.mark.parametrize("monitoring", ["True", "False"])
def test_get_machines_filter_multiple_valid(
    client, groupname, brand, connector, energy_status, monitoring
):
    """Test GET "/machines/" route with multiple valid filters."""
    response = client.get(f"/machines?group_name={groupname}&brand={brand}")
    assert response.status_code == HTTPStatus.HTTP_200_OK


# Test GET "/machines/" route with multiple invalid filters
@pytest.mark.parametrize("groupname", ["cloudE", "cloudF", "cloudG", "cloudH"])
@pytest.mark.parametrize(
    "brand", ["IBM Power 9", "IMB Power 10", "IBM Power 11", "IBM Power 12"]
)
@pytest.mark.parametrize("connector", ["test3", "test4"])
def test_get_machines_filter_multiple_invalid(client, groupname, brand, connector):
    """Test GET "/machines/" route with multiple invalid filters."""
    response = client.get(
        f"/machines?group_name={groupname}&brand={brand}&connector={connector}"
    )
    assert response.status_code == HTTPStatus.HTTP_200_OK


# Test GET "/machines/id={id}" route with an id that exists
@pytest.mark.parametrize("id", [1, 2, 3, 4])
def test_get_machines_id(client, id):
    """Test GET "/machines/id={id}" route with an id that exists."""
    response = client.get(f"/machines/id={id}")
    assert response.status_code == HTTPStatus.HTTP_200_OK


# Test GET "/machines/id={id}" route with an id that does not exist
@pytest.mark.parametrize("id", [100, 200, 300, 400])
def test_get_machines_id_not_exist(client, id):
    """Test GET "/machines/id={id}" route with an id that does not exist."""
    response = client.get(f"/machines/id={id}")
    assert response.status_code == HTTPStatus.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": f"Machine with ID: {id} not found"}


# Test GET "/machines/id={id}" route with an id that is not an integer
@pytest.mark.parametrize("id", ["test", "test2", "test3", "test4"])
def test_get_machines_id_not_int(client, id):
    """Test GET "/machines/id={id}" route with an id that is not an integer."""
    response = client.get(f"/machines/id={id}")
    assert response.status_code == HTTPStatus.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json() == {
        "detail": [
            {
                "loc": ["path", "id"],
                "msg": "value is not a valid integer",
                "type": "type_error.integer",
            }
        ]
    }


# Test GET "/machines/hostname={hostname}" route with a hostname that exists
@pytest.mark.parametrize("hostname", ["cloudA001", "cloudB01", "cloudC01", "cloudD1"])
def test_get_machines_hostname(client, hostname):
    """Test GET "/machines/hostname={hostname}" route with a hostname that exists."""
    response = client.get(f"/machines/hostname={hostname}")
    assert response.status_code == HTTPStatus.HTTP_200_OK


# Test GET "/machines/hostname={hostname}" route with a hostname that does not exist
@pytest.mark.parametrize("hostname", ["cloudE001", "cloudF01", "cloudG01", "cloudH01"])
def test_get_machines_hostname_not_exist(client, hostname):
    """Test GET "/machines/hostname={hostname}" route with a hostname that does not exist."""
    response = client.get(f"/machines/hostname={hostname}")
    assert response.status_code == HTTPStatus.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": f"Machine with hostname: {hostname} not found"}


# Test GET "/machines/hostname={hostname}" route with a hostname that is not a string
@pytest.mark.parametrize("hostname", [1, 2, 3, 4])
def test_get_machines_hostname_not_str(client, hostname):
    """Test GET "/machines/hostname={hostname}" route with a hostname that is not a string."""
    response = client.get(f"/machines/hostname={hostname}")
    assert response.status_code == HTTPStatus.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": f"Machine with hostname: {hostname} not found"}
