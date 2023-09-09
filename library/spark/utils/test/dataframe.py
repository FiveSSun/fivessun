import colorama
from pyspark import sql
from pyspark.sql import functions as F


def assert_dataframe_equals(
    dframe1: sql.DataFrame,
    dframe2: sql.DataFrame,
    order_by: str| list[str] | None = None,
    sort_array_col: bool = False,
):
    dframe1 = dframe1.select(sorted(dframe1.columns))
    dframe2 = dframe2.select(sorted(dframe2.columns))

    if order_by:
        if isinstance(order_by, str):
            order_by = [order_by]
        dframe1 = dframe1.orderBy(*order_by)
        dframe2 = dframe2.orderBy(*order_by)

    array_types_col = []
    map_types_col = []
    regular_col = []
    for col1_dtype, col2_dtype in zip(dframe1.dtypes, dframe2.dtypes):
        if col1_dtype != col2_dtype:
            df1_diff_set = set(dframe1.dtypes) - set(dframe2.dtypes)
            df2_diff_set = set(dframe2.dtypes) - set(dframe1.dtypes)
            print(colorama.Fore.MAGENTA + "dframe1 and dframe2's columns don't match." + colorama.Style.RESET_ALL)
            print(
                f"\ndframe1 columns contain: {dframe1.dtypes}\n\
                \ndframe2 columns contain: {dframe2.dtypes}\n"
            )
            print(colorama.Fore.RED + f"column type differences: {list(df1_diff_set | df2_diff_set)}")
            print(colorama.Style.RESET_ALL)
            assert False
        elif col1_dtype[1].startswith("array") and col2_dtype[1].startswith("array"):
            array_types_col.append((col1_dtype[0], col2_dtype[0]))
        elif "map" in col1_dtype[1] and "map" in col2_dtype[1]:
            map_types_col.append((col1_dtype[0], col2_dtype[0]))
        else:
            regular_col.append((col1_dtype[0], col2_dtype[0]))

    join_cond = []
    for df1_col, df2_col in regular_col:
        join_cond.append(dframe1[f"{df1_col}"].eqNullSafe(dframe2[f"{df2_col}"]))
    for df1_col, df2_col in map_types_col:
        join_cond.append(F.sort_array(F.map_entries(dframe1[f"{df1_col}"])).eqNullSafe(F.sort_array(F.map_entries(dframe2[f"{df2_col}"]))))

    diff1 = dframe1.join(dframe2, on=join_cond, how="left_anti")
    diff2 = dframe2.join(dframe1, on=join_cond, how="left_anti")
    if (diff1.count() > 0 or diff2.count()) > 0:
        print(colorama.Fore.GREEN + "Record which exists in dframe1, but doesn't exist in dframe2:")
        diff1.show(truncate=False)
        print(colorama.Fore.RED + "Record which exists in dframe2, but doesn't exist in dframe1:")
        diff2.show(truncate=False)
        print(colorama.Style.RESET_ALL)
        assert False

    if sort_array_col:
        for df1_col, df2_col in array_types_col:
            dframe1 = dframe1.withColumn(f"{df1_col}", F.sort_array(f"{df1_col}"))
            dframe2 = dframe2.withColumn(f"{df2_col}", F.sort_array(f"{df2_col}"))

    if dframe1.collect() != dframe2.collect():
        print(colorama.Fore.MAGENTA + "Two dataframes are somewhat different. Find the differences from below.")
        print(colorama.Fore.GREEN + "dframe1")
        dframe1.show(truncate=False)
        print(colorama.Fore.RED + "dframe2")
        dframe2.show(truncate=False)
        print(colorama.Style.RESET_ALL)
        assert False
