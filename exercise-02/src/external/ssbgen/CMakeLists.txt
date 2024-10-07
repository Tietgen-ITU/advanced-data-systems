add_library(psgen STATIC
    bcd2.c
    bm_utils.c
    build.c
    driver.c
    load_stub.c
    permute.c
    print.c
    qgen.c
    rnd.c
)

target_compile_definitions(psgen PUBLIC DB2)
target_compile_definitions(psgen PUBLIC MAC)
target_compile_definitions(psgen PUBLIC SSBM)
target_compile_definitions(psgen PUBLIC DBNAME="dss")