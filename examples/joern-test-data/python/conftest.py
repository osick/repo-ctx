"""
Test fixtures for DocGen tests.
"""

import pytest
from docgen.state import (
    DocGenState,
    DocGenOptions,
    Symbol,
    Dependency,
    Document,
    DomainModel,
    DomainEntity,
    DocSection,
    ReviewFeedback,
    create_initial_state,
)


@pytest.fixture
def sample_symbols() -> list[dict]:
    """Sample code symbols for testing."""
    return [
        Symbol(
            name="User",
            symbol_type="class",
            signature="class User",
            docstring="Represents a user in the system",
            file_path="src/models/user.py",
            line_number=10,
            visibility="public",
        ).to_dict(),
        Symbol(
            name="Order",
            symbol_type="class",
            signature="class Order",
            docstring="Represents a customer order",
            file_path="src/models/order.py",
            line_number=5,
            visibility="public",
        ).to_dict(),
        Symbol(
            name="create_user",
            symbol_type="function",
            signature="def create_user(name: str, email: str) -> User",
            docstring="Create a new user",
            file_path="src/services/user_service.py",
            line_number=20,
            visibility="public",
        ).to_dict(),
    ]


@pytest.fixture
def sample_dependencies() -> list[dict]:
    """Sample dependency relationships for testing."""
    return [
        Dependency(
            source="Order",
            target="User",
            dependency_type="uses",
        ).to_dict(),
        Dependency(
            source="UserService",
            target="User",
            dependency_type="creates",
        ).to_dict(),
    ]


@pytest.fixture
def sample_existing_docs() -> list[dict]:
    """Sample existing documentation for testing."""
    return [
        Document(
            title="README",
            content="""# Sample Project

A sample e-commerce application.

## Overview

This project is a simple e-commerce system that handles users and orders.

## Key Concepts

- **User** is a registered customer
- **Order** is a purchase made by a user
""",
            path="README.md",
            doc_type="readme",
        ).to_dict(),
    ]


@pytest.fixture
def sample_domain_model() -> dict:
    """Sample domain model for testing."""
    return DomainModel(
        entities=[
            DomainEntity(
                name="User",
                description="A registered customer in the system",
                related_symbols=["User", "create_user"],
                attributes=["name", "email"],
                relationships=["places Order"],
            ),
            DomainEntity(
                name="Order",
                description="A purchase made by a user",
                related_symbols=["Order"],
                attributes=["order_id", "items", "total"],
                relationships=["belongs to User"],
            ),
        ],
        processes=[
            {"name": "User Registration", "steps": ["Create user", "Send confirmation"]},
            {"name": "Order Placement", "steps": ["Select items", "Checkout", "Confirm"]},
        ],
        glossary={
            "User": "A registered customer",
            "Order": "A purchase transaction",
        },
    ).to_dict()


@pytest.fixture
def sample_state(
    sample_symbols,
    sample_dependencies,
    sample_existing_docs,
    sample_domain_model,
) -> DocGenState:
    """Create a sample workflow state for testing."""
    state = create_initial_state(
        target_path="./sample-project",
        output_path="./docs/generated",
    )

    state["symbols"] = sample_symbols
    state["dependencies"] = sample_dependencies
    state["existing_docs"] = sample_existing_docs
    state["domain_model"] = sample_domain_model
    state["terminology"] = {"User": "A registered customer", "Order": "A purchase"}

    return state


@pytest.fixture
def sample_documentation() -> list[dict]:
    """Sample generated documentation for testing."""
    return [
        DocSection(
            title="Overview",
            content="## Overview\n\nThis is a sample project documentation.",
            section_type="overview",
            order=0,
        ).to_dict(),
        DocSection(
            title="User",
            content="## User\n\nRepresents a customer.",
            section_type="entity",
            order=1,
        ).to_dict(),
    ]
