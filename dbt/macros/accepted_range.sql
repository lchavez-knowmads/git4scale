{% test accepted_range(model, column_name, min, max) %}

with validation_errors as (
    select
        {{ column_name }} as test_column
    from {{ model }}
    where {{ column_name }} < {{ min }}
       or {{ column_name }} > {{ max }}
)

select *
from validation_errors

{% endtest %}
