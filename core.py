import csv
import hashlib

from jinja2 import Environment, FileSystemLoader
import arrow
import requests

from colors import colors

env = Environment(loader=FileSystemLoader("templates"))

SOURCES = {
    "yearly": "ara0004.csv",
    "monthly": "ara0044.csv",
}
COLORS_BY_CODE = {}


def is_invalid_value(value):
    return not value or value == ".."


def int_or_none(value):
    if is_invalid_value(value):
        return None

    return int(value.replace(" ", ""))


def get_color_code(code):
    if code not in COLORS_BY_CODE:
        color = colors[len(COLORS_BY_CODE)]
        COLORS_BY_CODE[code] = color

    return COLORS_BY_CODE[code]


def parse_csv(filename, input_date_format, output_date_format):
    with open(filename, newline="", encoding="latin2") as f:
        reader = csv.reader(f, delimiter=";")

        # title
        next(reader)

        _, _, *date_strings = next(reader)

        dates = [
            arrow.get(date, input_date_format, locale="hu-hu").format(
                output_date_format, locale="hu-hu"
            )
            for date in date_strings
        ]

        rows_without_values = [0] * len(dates)

        data = []
        for idx, row in enumerate(reader):
            code, name, *values = row
            # long dash(?) is not getting decoded properly
            name = name.replace(chr(150), "–")

            prices = list(map(int_or_none, values))

            for p_idx, price in enumerate(prices):
                if not price:
                    rows_without_values[p_idx] += 1

            data.append(
                {
                    "code": code,
                    "label": name,
                    "prices": prices,
                    "color": get_color_code(code),
                }
            )

        # if we have a column where we missin all data all the rest is probably empty too
        try:
            first = rows_without_values.index(len(data))
            dates = dates[:first]
            for d in data:
                d["prices"] = d["prices"][:first]
        except ValueError:
            pass

    return {
        "dates": dates,
        "data": data,
    }


def get_context_data():
    monthly = parse_csv(f"sources/stadat-{SOURCES['monthly']}", "YYYY. MMMM", "YYYY. MMM")
    yearly = parse_csv(f"sources/stadat-{SOURCES['yearly']}", "YYYY", "YYYY")

    return {
        "monthly": monthly,
        "yearly": yearly,
        "last_update": arrow.utcnow().format("YYYY-MM-DD"),
    }


def build():
    templates = ["eves.jinja", "havi.jinja", "index.jinja"]

    context = get_context_data()

    for template in templates:
        content = env.get_template(template).render(**context)
        name = template.replace(".jinja", ".html")
        with open("build/" + name, "w") as f:
            f.write(content)


def update():
    for name in SOURCES.values():
        response = requests.get(f"https://www.ksh.hu/stadat_files/ara/hu/{name}")
        response.raise_for_status()

        online_hash = hashlib.sha256(response.content).hexdigest()
        with open(f"sources/stadat-{name}", "rb") as f:
            repo_hash = hashlib.sha256(f.read()).hexdigest()

        if online_hash == repo_hash:
            continue

        print(f"Found new version for {name}")
        with open(f"sources/stadat-{name}", "wb") as f:
            f.write(response.content)


if __name__ == "__main__":
    update()
    build()
