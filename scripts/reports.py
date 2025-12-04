import os
import json
import csv
import psycopg2
import matplotlib.pyplot as plt

# ---------- Paths ----------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "db_config.json")

REPORTS_DIR = os.path.join(BASE_DIR, "reports")
MANAGERIAL_DIR = os.path.join(REPORTS_DIR, "managerial_reports")

os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(MANAGERIAL_DIR, exist_ok=True)


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

def save_csv(headers, rows, filename, folder=REPORTS_DIR):
    csv_path = os.path.join(folder, filename)
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


# ---------- Ceremony type mapping ----------

def map_ceremony_to_type(ceremony_name: str) -> str:
    if not ceremony_name:
        return "OTHER"

    name_lower = ceremony_name.lower()
    if "business" in name_lower:
        return "BUS"
    if "engineer" in name_lower:
        return "ENG"
    if "science" in name_lower:
        return "SCI"
    if "art" in name_lower:
        return "ART"
    return "OTHER"


# ---------- Generic pie chart helper ----------

def make_pie_chart(labels, values, title, legend_title, filename, folder=REPORTS_DIR):
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

    img_path = os.path.join(folder, filename)
    fig.savefig(img_path, dpi=200, bbox_inches="tight")
    plt.close(fig)

    print(f"Saved chart: {img_path}")


# ---------- Managerial aggregate reports + charts ----------

def build_managerial_reports():
    """
    Build a CSV with high-level aggregate statistics
    and create bar charts for managers under reports/managerial_reports. [web:99][web:155][web:168]
    """
    conn = get_connection()
    cur = conn.cursor()

    rows = []

    # 1) Overall student counts and biometric opt-in
    cur.execute("""
        SELECT
            COUNT(*) AS total_students,
            SUM(CASE WHEN opt_in_biometric = TRUE THEN 1 ELSE 0 END) AS total_opt_in,
            SUM(CASE WHEN opt_in_biometric = FALSE THEN 1 ELSE 0 END) AS total_not_opt_in
        FROM STUDENT;
    """)
    total_students, total_opt_in, total_not_opt_in = cur.fetchone()
    rows.append([
        "Overall Students and Opt-In",
        "COUNT, SUM",
        total_students,
        "", "", "", "",
        total_opt_in,
        total_not_opt_in,
        ""
    ])

    # 2) Min/avg/max number of students per degree
    cur.execute("""
        SELECT
            MIN(num_students),
            MAX(num_students),
            AVG(num_students),
            COUNT(*),
            SUM(num_students)
        FROM (
            SELECT degree_name, COUNT(*) AS num_students
            FROM STUDENT
            GROUP BY degree_name
        ) t;
    """)
    min_deg, max_deg, avg_deg, count_deg_groups, sum_deg = cur.fetchone()
    rows.append([
        "Students per Degree (distribution)",
        "MIN, MAX, AVG, COUNT, SUM of grouped counts",
        count_deg_groups,
        min_deg,
        max_deg,
        avg_deg,
        sum_deg,
        "", "", ""
    ])

    # 3) Min/avg/max number of students per ceremony
    cur.execute("""
        SELECT
            MIN(num_students),
            MAX(num_students),
            AVG(num_students),
            COUNT(*),
            SUM(num_students)
        FROM (
            SELECT
                C.ceremony_id,
                COUNT(S.PID) AS num_students
            FROM CEREMONY C
            LEFT JOIN DEGREE D ON D.ceremony_id = C.ceremony_id
            LEFT JOIN STUDENT S ON S.degree_name = D.degree_name
            GROUP BY C.ceremony_id
        ) t;
    """)
    min_cer, max_cer, avg_cer, count_cer_groups, sum_cer = cur.fetchone()
    rows.append([
        "Students per Ceremony (distribution)",
        "MIN, MAX, AVG, COUNT, SUM of grouped counts",
        count_cer_groups,
        min_cer,
        max_cer,
        avg_cer,
        sum_cer,
        "", "", ""
    ])

    # 4) Min/avg/max number of students per degree type
    cur.execute("""
        SELECT
            MIN(num_students),
            MAX(num_students),
            AVG(num_students),
            COUNT(*),
            SUM(num_students)
        FROM (
            SELECT degree_type, COUNT(*) AS num_students
            FROM STUDENT
            GROUP BY degree_type
        ) t;
    """)
    min_dtype, max_dtype, avg_dtype, count_dtype_groups, sum_dtype = cur.fetchone()
    rows.append([
        "Students per Degree Type (distribution)",
        "MIN, MAX, AVG, COUNT, SUM of grouped counts",
        count_dtype_groups,
        min_dtype,
        max_dtype,
        avg_dtype,
        sum_dtype,
        "", "", ""
    ])

    # 5) Min/avg/max queued entries per ceremony
    cur.execute("""
        SELECT
            MIN(num_entries),
            MAX(num_entries),
            AVG(num_entries),
            COUNT(*),
            SUM(num_entries)
        FROM (
            SELECT ceremony_id, COUNT(*) AS num_entries
            FROM QUEUED
            GROUP BY ceremony_id
        ) t;
    """)
    min_q, max_q, avg_q, count_q_groups, sum_q = cur.fetchone()
    rows.append([
        "Queued Entries per Ceremony (distribution)",
        "MIN, MAX, AVG, COUNT, SUM of grouped counts",
        count_q_groups,
        min_q,
        max_q,
        avg_q,
        sum_q,
        "", "", ""
    ])

    cur.close()
    conn.close()

    # Save managerial CSV
    headers = [
        "report_name",
        "description",
        "group_count_or_total_count",
        "min_value",
        "max_value",
        "avg_value",
        "sum_value",
        "extra_1",
        "extra_2",
        "extra_3"
    ]
    save_csv(headers, rows, "managerial_reports.csv", folder=MANAGERIAL_DIR)

    # Create simple bar charts from these aggregates
    # 1) Overall Students & Opt-in breakdown
    fig, ax = plt.subplots(figsize=(8, 5))
    categories = ["Total Students", "Opt-in", "Not Opt-in"]
    values = [total_students, total_opt_in or 0, total_not_opt_in or 0]
    bars = ax.bar(categories, values)
    ax.set_title("Overall Students and Biometric Opt-in")
    ax.set_ylabel("Count")

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height,
                f"{int(height)}", ha="center", va="bottom")
    img_path = os.path.join(MANAGERIAL_DIR, "overall_students_optin.png")
    fig.savefig(img_path, dpi=200, bbox_inches="tight")
    plt.close(fig)

    # 2) Students per Degree: min/avg/max
    fig, ax = plt.subplots(figsize=(8, 5))
    categories = ["Min per Degree", "Avg per Degree", "Max per Degree"]
    values = [min_deg or 0, float(avg_deg or 0), max_deg or 0]
    bars = ax.bar(categories, values)
    ax.set_title("Students per Degree (Min/Avg/Max)")
    ax.set_ylabel("Students")

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height,
                f"{height:.1f}", ha="center", va="bottom")
    img_path = os.path.join(MANAGERIAL_DIR, "students_per_degree_stats.png")
    fig.savefig(img_path, dpi=200, bbox_inches="tight")
    plt.close(fig)

    # 3) Students per Ceremony: min/avg/max
    fig, ax = plt.subplots(figsize=(8, 5))
    categories = ["Min per Ceremony", "Avg per Ceremony", "Max per Ceremony"]
    values = [min_cer or 0, float(avg_cer or 0), max_cer or 0]
    bars = ax.bar(categories, values)
    ax.set_title("Students per Ceremony (Min/Avg/Max)")
    ax.set_ylabel("Students")

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height,
                f"{height:.1f}", ha="center", va="bottom")
    img_path = os.path.join(MANAGERIAL_DIR, "students_per_ceremony_stats.png")
    fig.savefig(img_path, dpi=200, bbox_inches="tight")
    plt.close(fig)

    # 4) Students per Degree Type: min/avg/max
    fig, ax = plt.subplots(figsize=(8, 5))
    categories = ["Min per Degree Type", "Avg per Degree Type", "Max per Degree Type"]
    values = [min_dtype or 0, float(avg_dtype or 0), max_dtype or 0]
    bars = ax.bar(categories, values)
    ax.set_title("Students per Degree Type (Min/Avg/Max)")
    ax.set_ylabel("Students")

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height,
                f"{height:.1f}", ha="center", va="bottom")
    img_path = os.path.join(MANAGERIAL_DIR, "students_per_degree_type_stats.png")
    fig.savefig(img_path, dpi=200, bbox_inches="tight")
    plt.close(fig)

    # 5) Queued Entries per Ceremony: min/avg/max
    fig, ax = plt.subplots(figsize=(8, 5))
    categories = ["Min Queued/Ceremony", "Avg Queued/Ceremony", "Max Queued/Ceremony"]
    values = [min_q or 0, float(avg_q or 0), max_q or 0]
    bars = ax.bar(categories, values)
    ax.set_title("Queued Entries per Ceremony (Min/Avg/Max)")
    ax.set_ylabel("Queued Entries")

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height,
                f"{height:.1f}", ha="center", va="bottom")
    img_path = os.path.join(MANAGERIAL_DIR, "queued_per_ceremony_stats.png")
    fig.savefig(img_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


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

    # 5) Students per ceremony (BUS/ENG/SCI/ART labels)
    cer_labels, cer_values, cer_rows = get_students_per_ceremony()
    save_csv(
        headers=["ceremony_name", "num_students"],
        rows=cer_rows,
        filename="students_per_ceremony.csv",
    )

    if cer_labels and cer_values:
        cer_type_labels = [map_ceremony_to_type(name) for name in cer_labels]

        fig, ax = plt.subplots(figsize=(10, 5))

        wedges, text_labels, autotexts = ax.pie(
            cer_values,
            labels=cer_type_labels,
            startangle=90,
            autopct="%1.1f%%",
            rotatelabels=True,
            labeldistance=1.05
        )

        plt.subplots_adjust(left=0.05, right=0.7)

        ax.legend(
            wedges,
            cer_labels,
            title="Ceremony",
            loc="center left",
            bbox_to_anchor=(1.0, 0.5),
            borderaxespad=0.0,
        )

        ax.set_title("Students per Ceremony")
        ax.axis("equal")

        img_path = os.path.join(REPORTS_DIR, "students_per_ceremony.png")
        fig.savefig(img_path, dpi=200, bbox_inches="tight")
        plt.close(fig)
        print(f"Saved chart: {img_path}")
    else:
        print("No data found for chart: Students per Ceremony")

    # Managerial aggregate statistics + charts
    build_managerial_reports()


if __name__ == "__main__":
    main()
