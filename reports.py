import os
import json
import csv
import psycopg2
import matplotlib.pyplot as plt

# ---------- Paths ----------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "db_config.json")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

os.makedirs(REPORTS_DIR, exist_ok=True)


# ---------- Load DB config from JSON ----------

def load_db_config_from_json():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    required_keys = ["dbname", "user", "password", "host", "port"]
    for key in required_keys:
        if key not in config or not config[key]:
            raise ValueError(f"Missing '{key}' in db_config.json")

    return config


DB_CONFIG = load_db_config_from_json()


# ---------- DB helpers ----------

def get_connection():
    return psycopg2.connect(**DB_CONFIG)


# ---------- CSV helper ----------

def save_csv(headers, rows, filename):
    csv_path = os.path.join(REPORTS_DIR, filename)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    print(f"Saved CSV: {csv_path}")


# ---------- Data fetch functions ----------

def get_students_per_degree():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT degree_name, COUNT(*) AS num_students
        FROM STUDENT
        GROUP BY degree_name
        ORDER BY num_students DESC;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    labels, values, cleaned_rows = [], [], []
    for degree_name, count in rows:
        label = degree_name if degree_name is not None else "Unknown"
        labels.append(label)
        values.append(count)
        cleaned_rows.append([label, count])
    return labels, values, cleaned_rows


def get_queued_status_breakdown():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT status, COUNT(*) AS num_entries
        FROM QUEUED
        GROUP BY status
        ORDER BY num_entries DESC;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    labels, values, cleaned_rows = [], [], []
    for status, count in rows:
        label = status if status is not None else "Unknown"
        labels.append(label)
        values.append(count)
        cleaned_rows.append([label, count])
    return labels, values, cleaned_rows


def get_students_per_degree_type():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT degree_type, COUNT(*) AS num_students
        FROM STUDENT
        GROUP BY degree_type
        ORDER BY num_students DESC;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    labels, values, cleaned_rows = [], [], []
    for degree_type, count in rows:
        label = degree_type if degree_type is not None else "Unknown"
        labels.append(label)
        values.append(count)
        cleaned_rows.append([label, count])
    return labels, values, cleaned_rows


def get_biometric_opt_in_breakdown():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT opt_in_biometric, COUNT(*) AS num_students
        FROM STUDENT
        GROUP BY opt_in_biometric
        ORDER BY num_students DESC;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    labels, values, cleaned_rows = [], [], []
    for opt_in, count in rows:
        if opt_in is True:
            label = "Opt-in"
        elif opt_in is False:
            label = "Not Opt-in"
        else:
            label = "Unknown"
        labels.append(label)
        values.append(count)
        cleaned_rows.append([label, count])
    return labels, values, cleaned_rows


def get_students_per_ceremony():
    """
    Uses STUDENT -> DEGREE -> CEREMONY to count students per ceremony.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            C.name AS ceremony_name,
            COUNT(S.PID) AS num_students
        FROM CEREMONY C
        LEFT JOIN DEGREE D ON D.ceremony_id = C.ceremony_id
        LEFT JOIN STUDENT S ON S.degree_name = D.degree_name
        GROUP BY C.name
        ORDER BY num_students DESC;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    labels, values, cleaned_rows = [], [], []
    for ceremony_name, count in rows:
        label = ceremony_name if ceremony_name is not None else "Unknown"
        labels.append(label)
        values.append(count)
        cleaned_rows.append([label, count])
    return labels, values, cleaned_rows


# ---------- Chart helper ----------

def make_pie_chart(labels, values, title, legend_title, filename):
    if not labels or not values:
        print(f"No data found for chart: {title}")
        return

    slice_labels = [str(lbl)[:3].upper() for lbl in labels]

    fig, ax = plt.subplots(figsize=(10, 5))

    wedges, text_labels, autotexts = ax.pie(
        values,
        labels=slice_labels,
        startangle=90,
        autopct="%1.1f%%",
        rotatelabels=True,
        labeldistance=1.05
    )

    plt.subplots_adjust(left=0.05, right=0.7)

    ax.legend(
        wedges,
        labels,
        title=legend_title,
        loc="center left",
        bbox_to_anchor=(1.0, 0.5),
        borderaxespad=0.0,
    )

    ax.set_title(title)
    ax.axis("equal")

    img_path = os.path.join(REPORTS_DIR, filename)
    fig.savefig(img_path, dpi=200, bbox_inches="tight")
    plt.close(fig)

    print(f"Saved chart: {img_path}")


# ---------- Entry point ----------

def main():
    # 1) Students per degree
    degree_labels, degree_values, degree_rows = get_students_per_degree()
    save_csv(
        headers=["degree_name", "num_students"],
        rows=degree_rows,
        filename="students_per_degree.csv",
    )
    make_pie_chart(
        degree_labels,
        degree_values,
        title="Students per Degree",
        legend_title="Degree",
        filename="students_per_degree.png",
    )

    # 2) QUEUED status breakdown
    status_labels, status_values, status_rows = get_queued_status_breakdown()
    save_csv(
        headers=["status", "num_entries"],
        rows=status_rows,
        filename="queued_status_breakdown.csv",
    )
    make_pie_chart(
        status_labels,
        status_values,
        title="Queued Status Breakdown",
        legend_title="Status",
        filename="queued_status_breakdown.png",
    )

    # 3) Students per degree type
    dtype_labels, dtype_values, dtype_rows = get_students_per_degree_type()
    save_csv(
        headers=["degree_type", "num_students"],
        rows=dtype_rows,
        filename="students_per_degree_type.csv",
    )
    make_pie_chart(
        dtype_labels,
        dtype_values,
        title="Students per Degree Type",
        legend_title="Degree Type",
        filename="students_per_degree_type.png",
    )

    # 4) Biometric opt-in vs not
    bio_labels, bio_values, bio_rows = get_biometric_opt_in_breakdown()
    save_csv(
        headers=["opt_in_status", "num_students"],
        rows=bio_rows,
        filename="biometric_opt_in.csv",
    )
    make_pie_chart(
        bio_labels,
        bio_values,
        title="Biometric Opt-in Status",
        legend_title="Opt-in Status",
        filename="biometric_opt_in.png",
    )

    # 5) Students per ceremony
    cer_labels, cer_values, cer_rows = get_students_per_ceremony()
    save_csv(
        headers=["ceremony_name", "num_students"],
        rows=cer_rows,
        filename="students_per_ceremony.csv",
    )
    make_pie_chart(
        cer_labels,
        cer_values,
        title="Students per Ceremony",
        legend_title="Ceremony",
        filename="students_per_ceremony.png",
    )


if __name__ == "__main__":
    main()
