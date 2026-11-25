# APEX Session State and SQL Performance

Review `V()`, `NV()` and `APEX_SESSION_STATE` calls inside SQL predicates. A direct PL/SQL getter can run repeatedly as Oracle evaluates rows. A bind avoids those calls and lets the optimizer consider the value during a hard parse when bind peeking applies. Statistics and data skew can change cardinality estimates, index access and join choices. Test both selective and common values.

The examples assume an application-owned `orders` table with `order_id`, `owner_name` and `status`. Keep the application's authentication, row authorization and tenant scope in each equivalent query.

## SQL and PL/SQL Run by APEX

Use `:APP_USER` and item binds in region SQL, LOVs, chart queries, processes and validations. For an AJAX refresh, submit the filter item through the component's Items to Submit. Match bind types to the target columns. Convert numeric or date values explicitly where needed and keep conversions off indexed columns when possible.

```sql
select o.order_id, o.status
  from orders o
 where o.owner_name = :APP_USER
   and o.status = :P10_STATUS
```

## Stored PL/SQL Packages

Pass session values into typed parameters. The APEX process below calls a function declared in the package specification.

```sql
begin
    :P10_ORDER_COUNT := order_query_pkg.count_for_owner(p_owner => :APP_USER);
end;
```

Implement the member in the package body. Supply `p_owner` from the authenticated server-side identity and keep authorization checks required by the application at the trusted entry point.

```sql
function count_for_owner(p_owner in orders.owner_name%type) return number is
    l_count number;
begin
    select count(*)
      into l_count
      from orders o
     where o.owner_name = p_owner;

    return l_count;
end count_for_owner;
```

When an APEX-specific routine must read session state itself, declare `l_owner orders.owner_name%type := v('APP_USER');` once before SQL and filter with `o.owner_name = l_owner`. Use a typed session-state getter where the item requires it. For a legacy SQL expression that must retain `V()`, Oracle documents the scalar subquery `(select v('APP_USER') from dual)` to reduce repeated evaluation. Both that subquery and `SYS_CONTEXT` can reduce getter overhead. Bind peeking still applies only to bind variables. Keep session-dependent functions free of `DETERMINISTIC` because their results depend on the session.

## Views

Use the documented `APEX$SESSION` context when a view must enforce the application identity itself. APEX sets the context for the request. With literal arguments in SQL, Oracle evaluates `SYS_CONTEXT` once per execution per call site. Use documented attributes such as `APP_USER` and use session-state APIs or binds for arbitrary page and application items.

```sql
create or replace view my_orders_v as
select o.order_id, o.status
  from orders o
 where o.owner_name = sys_context('APEX$SESSION', 'APP_USER');
```

When the consuming server-side query already owns the authorization boundary, a bind filter such as `where o.owner_name = :APP_USER` can also be applied when selecting from a reusable view. Oracle can push that predicate into the view when the query permits it. Check the executed plan for predicate placement. Preserve security predicates in views that enforce row scope for their callers. Test with two identities and with missing context to verify the expected row visibility.

## Compare Executed Plans

1. In authorized DEV or test, use the same data, parsing schema, effective identity, bind type and filter value for both variants. Compare `V()` and `SYS_CONTEXT` in an initialized APEX context. For SQLcl, use an approved test session and verify that `V('APP_USER')` and `SYS_CONTEXT('APEX$SESSION', 'APP_USER')` resolve to the same expected, non-null identity. `APEX_SESSION.CREATE_SESSION` runs application initialization code, so review its effects before using it and clean up any test session you create.
2. Run each query to completion and check that it returns the same rows. Capture the cursor plan immediately after each execution. In the SQLcl example, `:b_owner` is the client equivalent of the APEX bind. `SET SERVEROUTPUT OFF` avoids client output retrieval between the query and its plan capture.

   ```sql
   set serveroutput off
   variable b_owner varchar2(255)
   exec :b_owner := v('APP_USER');

   select /*+ gather_plan_statistics */ /* apex-v-test-direct */ o.order_id
     from orders o
    where o.owner_name = v('APP_USER');

   select plan_table_output
     from table(dbms_xplan.display_cursor(null, null, 'ALLSTATS LAST +PREDICATE'));

   select /*+ gather_plan_statistics */ /* apex-v-test-bind */ o.order_id
     from orders o
    where o.owner_name = :b_owner;

   select plan_table_output
     from table(dbms_xplan.display_cursor(null, null, 'ALLSTATS LAST +PREDICATE'));
   ```

3. Verify that each plan shows the intended statement. If the client runs intervening SQL, find your tagged statement in `V$SQL` with approved diagnostic access. Identify the child cursor used for the execution and pass its `SQL_ID` and `CHILD_NUMBER` to `DBMS_XPLAN.DISPLAY_CURSOR` with the same format. `DISPLAY_CURSOR` needs access to the relevant fixed views. If actual statistics are unavailable, record that limitation. `EXPLAIN PLAN` provides estimates only.
4. Compare access and filter predicates, scan and join operations, `E-Rows` against `A-Rows` (account for `Starts`), `Buffers`, and elapsed time over repeated comparable runs. For a view or a scalar subquery, repeat the comparison with the same projection and filters. Lower elapsed time with the same scan can reflect fewer getter calls. A different estimate, access path or join order can reflect bind peeking and data distribution. Verify the result in the actual APEX render or AJAX flow as well.

## References

- [APEX 26.2 session state](https://docs.oracle.com/en/database/oracle/apex/26.2/htmdb/managing-session-state-values.html), [built-in context attributes](https://docs.oracle.com/en/database/oracle/apex/26.2/htmdb/using-available-built-in-substitution-strings.html) and [test session creation](https://docs.oracle.com/en/database/oracle/apex/26.2/aeapi/CREATE_SESSION-Procedure.html).
- [Oracle `SYS_CONTEXT`](https://docs.oracle.com/en/database/oracle/oracle-database/26/sqlrf/SYS_CONTEXT.html) and [`DETERMINISTIC` rules](https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/DETERMINISTIC-clause.html).
- [Oracle cursor sharing](https://docs.oracle.com/en/database/oracle/oracle-database/26/tgsql/improving-rwp-cursor-sharing.html) and [`DBMS_XPLAN`](https://docs.oracle.com/en/database/oracle/oracle-database/26/arpls/DBMS_XPLAN.html).
- [John Scott's APEX experiments](https://jes-dev.hashnode.dev/improve-the-performance-of-almost-any-apex-application).
