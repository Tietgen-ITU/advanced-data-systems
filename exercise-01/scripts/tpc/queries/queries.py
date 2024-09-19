query1 = """
select
    l_returnflag,
    l_linestatus,
    sum(l_quantity) as sum_qty,
    sum(l_extendedprice) as sum_base_price,
    sum(l_extendedprice*(1-l_discount)) as sum_disc_price,
    sum(l_extendedprice*(1-l_discount)*(1+l_tax)) as sum_charge,
    avg(l_quantity) as avg_qty,
    avg(l_extendedprice) as avg_price,
    avg(l_discount) as avg_disc,
    count(*) as count_order
from lineitem
where l_shipdate <= DATEADD(DAY, -90, DATE '1998-12-01')
group by l_returnflag, l_linestatus
order by l_returnflag, l_linestatus;
"""

query5 = """
select
    n_name,
    sum(l_extendedprice * (1 - l_discount)) as revenue
    from
    customer,
    orders,
    lineitem,
    supplier,
    nation,
    region
where
    c_custkey = o_custkey
    and l_orderkey = o_orderkey
    and l_suppkey = s_suppkey
    and c_nationkey = s_nationkey
    and s_nationkey = n_nationkey
    and n_regionkey = r_regionkey
    and r_name = 'ASIA'
    and o_orderdate >= '1997-01-01'
    and o_orderdate < DATEADD(YEAR, 1, '1997-01-01')
group by n_name
order by revenue desc;
"""

query18 = """
select
    c_name,
    c_custkey,
    o_orderkey,
    o_orderdate,
    o_totalprice,
    sum(l_quantity)
    from
    customer,
    orders,
    lineitem
where o_orderkey in (select l_orderkey 
                        from lineitem
                        group by l_orderkey 
                        having sum(l_quantity) > 314)
    and c_custkey = o_custkey
    and o_orderkey = l_orderkey
group by
    c_name,
    c_custkey,
    o_orderkey,
    o_orderdate,
    o_totalprice
order by o_totalprice desc, o_orderdate;
"""

benchmark_queries = [query1, query5, query18]