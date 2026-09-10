from contact_service import ContactRequest, route_contact


def test_order_contact_is_routed_to_team_with_order_subject():
    result = route_contact(ContactRequest("Ari", "ari@example.com", "Need an update", "ORD-7"), "ops@example.com")
    assert result["to"] == "ops@example.com"
    assert result["subject"] == "Order ORD-7: customer contact"
    assert "Need an update" in result["body"]
