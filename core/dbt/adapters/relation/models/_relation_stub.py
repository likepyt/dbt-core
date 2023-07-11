"""
This module provides a way to store only the required metadata for a `Relation` without any parsers or actual
relation_type-specific subclasses. It's primarily used to represent a relation that exists in the database
without needing to query the database. This is useful with low attribution macros (e.g. `drop_sql`, `rename_sql`)
where the details are not needed to perform the action. It should be the case that if a macro supports execution
with a `RelationStub` instance, then it should also support execution with a `Relation` instance. The converse
is not true (e.g. `create_sql`).
"""
from dataclasses import dataclass

from dbt.contracts.graph.nodes import ModelNode

from dbt.adapters.relation.models._database import DatabaseRelation
from dbt.adapters.relation.models._policy import RenderPolicy
from dbt.adapters.relation.models._relation import Relation
from dbt.adapters.relation.models._relation_component import DescribeRelationResults
from dbt.adapters.relation.models._schema import SchemaRelation


@dataclass(frozen=True)
class DatabaseRelationStub(DatabaseRelation):
    @classmethod
    def from_dict(cls, config_dict) -> "DatabaseRelationStub":
        database_stub = cls(
            **{
                "name": config_dict["name"],
                "render": config_dict["render"],
            }
        )
        assert isinstance(database_stub, DatabaseRelationStub)
        return database_stub

    @classmethod
    def parse_model_node(cls, model_node: ModelNode) -> dict:
        return {}

    @classmethod
    def parse_describe_relation_results(
        cls, describe_relation_results: DescribeRelationResults
    ) -> dict:
        return {}


@dataclass(frozen=True)
class SchemaRelationStub(SchemaRelation):
    render: RenderPolicy

    @classmethod
    def from_dict(cls, config_dict) -> "SchemaRelationStub":
        schema_stub = cls(
            **{
                "name": config_dict["name"],
                "database": DatabaseRelation.from_dict(config_dict["database"]),
                "render": config_dict["render"],
                "DatabaseParser": DatabaseRelationStub,
            }
        )
        assert isinstance(schema_stub, SchemaRelationStub)
        return schema_stub

    @classmethod
    def parse_model_node(cls, model_node: ModelNode) -> dict:
        return {}

    @classmethod
    def parse_describe_relation_results(
        cls, describe_relation_results: DescribeRelationResults
    ) -> dict:
        return {}


@dataclass(frozen=True)
class RelationStub(Relation):
    can_be_renamed: bool

    @classmethod
    def from_dict(cls, config_dict) -> "RelationStub":
        relation_stub = cls(
            **{
                "name": config_dict["name"],
                "schema": SchemaRelationStub.from_dict(config_dict["schema"]),
                "render": config_dict["render"],
                "type": config_dict["type"],
                "can_be_renamed": config_dict["can_be_renamed"],
                "SchemaParser": SchemaRelationStub,
            }
        )
        assert isinstance(relation_stub, RelationStub)
        return relation_stub

    @classmethod
    def parse_model_node(cls, model_node: ModelNode) -> dict:
        return {}

    @classmethod
    def parse_describe_relation_results(
        cls, describe_relation_results: DescribeRelationResults
    ) -> dict:
        return {}
