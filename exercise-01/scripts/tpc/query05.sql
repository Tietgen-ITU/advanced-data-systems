ALTER SESSION SET USE_CACHED_RESULT = FALSE;

set region = 'ASIA';
set query_date = '1997-01-01'

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
    and r_name = $region
    and o_orderdate >= $query_date
    and o_orderdate < DATEADD(YEAR, 1, $query_date)
group by n_name
order by revenue desc;