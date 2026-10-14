-- Cross-database type helpers so the same models compile on DuckDB (CI/local)
-- and BigQuery (production).

{% macro numeric_type() %}
    {{ return(adapter.dispatch('numeric_type')()) }}
{% endmacro %}

{% macro default__numeric_type() %}numeric{% endmacro %}
{% macro duckdb__numeric_type() %}decimal(18,4){% endmacro %}

{% macro string_type() %}
    {{ return(adapter.dispatch('string_type')()) }}
{% endmacro %}

{% macro default__string_type() %}string{% endmacro %}
{% macro duckdb__string_type() %}varchar{% endmacro %}
