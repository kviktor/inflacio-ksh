import csv

from jinja2 import Environment, FileSystemLoader
import arrow

from colors import colors

env = Environment(
    loader=FileSystemLoader("templates"),
)


def is_invalid_value(value):
    return not value or value == ".."


def int_or_none(value):
    if is_invalid_value(value):
        return None

    return int(value.replace(" ", ""))


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
                    "color": colors[idx],
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
    yearly = parse_csv("sources/stadat-ara0004-1.1.1.4-hu.csv", "YYYY", "YYYY")
    monthly = parse_csv(
        "sources/stadat-ara0044-1.2.1.6-hu.csv", "YYYY. MMMM", "YYYY. MMM"
    )

    return {
        "yearly": yearly,
        "monthly": monthly,
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


if __name__ == "__name__":
    build()
