import datetime


def get_date_from_filename(fname: str):
    fname_parts = fname.split('.')
    for idx, part in enumerate(fname_parts):
        if 'MOD' in part:
            next_part = fname_parts[idx + 1]
            next_pt_len = len(next_part)
            if next_pt_len == 8 and next_part.startswith('A'):
                julian_date = next_part[1:]
                return julian_date
    return 0


def convert_date(julian_date: str):
    string_len = len(julian_date)
    assert string_len == 7
    standard_date = datetime.datetime.strptime(julian_date, '%Y%j').date()
    return standard_date.year, standard_date.month, standard_date.day
    # return standard_date_tuple


if __name__ == "__main__":
    test_name = 'data/MOD11B3.A2016214.h18v03.006.2016286174219.hdf'
    julian_date = get_date_from_filename(test_name)
    standard_date = convert_date(julian_date)
    print(standard_date)
