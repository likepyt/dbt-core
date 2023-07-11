from typing import Dict, List, Optional

from dbt.adapters.relation.models import Relation, RelationStub
from dbt.tests.util import read_file, write_file


def query_relation_type(project, relation: RelationStub) -> Optional[str]:
    sql = f"""
    select 'table' as relation_type
    from pg_tables
    where schemaname = '{relation.schema_name}'
    and tablename = '{relation.name}'
    union all
    select 'view' as relation_type
    from pg_views
    where schemaname = '{relation.schema_name}'
    and viewname = '{relation.name}'
    union all
    select 'materialized_view' as relation_type
    from pg_matviews
    where schemaname = '{relation.schema_name}'
    and matviewname = '{relation.name}'
    """
    results = project.run_sql(sql, fetch="all")
    if len(results) == 0:
        return None
    elif len(results) > 1:
        raise ValueError(f"More than one instance of {relation.name} found!")
    else:
        return results[0][0]


def query_row_count(project, relation: RelationStub) -> int:
    sql = f"select count(*) from {relation.fully_qualified_path};"
    return project.run_sql(sql, fetch="one")[0]


def query_indexes(project, relation: RelationStub) -> List[Dict[str, str]]:
    # pulled directly from `postgres__describe_indexes_template` and manually verified
    sql = f"""
        select
            i.relname                                   as name,
            m.amname                                    as method,
            ix.indisunique                              as "unique",
            array_to_string(array_agg(a.attname), ',')  as column_names
        from pg_index ix
        join pg_class i
            on i.oid = ix.indexrelid
        join pg_am m
            on m.oid=i.relam
        join pg_class t
            on t.oid = ix.indrelid
        join pg_namespace n
            on n.oid = t.relnamespace
        join pg_attribute a
            on a.attrelid = t.oid
            and a.attnum = ANY(ix.indkey)
        where t.relname ilike '{ relation.name }'
          and n.nspname ilike '{ relation.schema_name }'
          and t.relkind in ('r', 'm')
        group by 1, 2, 3
        order by 1, 2, 3
    """
    raw_indexes = project.run_sql(sql, fetch="all")
    indexes = [
        {
            header: value
            for header, value in zip(["name", "method", "unique", "column_names"], index)
        }
        for index in raw_indexes
    ]
    return indexes


def get_model_file(project, relation: Relation) -> str:
    return read_file(project.project_root, "models", f"{relation.name}.sql")


def set_model_file(project, relation: Relation, model_sql: str):
    write_file(model_sql, project.project_root, "models", f"{relation.name}.sql")
