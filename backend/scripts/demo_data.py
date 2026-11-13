import math

import numpy as np



def demo_rows():
    rng = np.random.default_rng(1022)
    rows = []
    for index in range(2800):
        age = int(rng.integers(1, 14))
        seniority = int(rng.integers(1, 20))
        alerts = int(rng.poisson(2.1))
        days = int(rng.integers(1, 180))
        usage = float(rng.normal(7.5, 2.4))
        risk = .34 * age - .18 * seniority + .61 * alerts + .018 * days - .21 * usage - 1.3
        late = int(rng.random() < 1 / (1 + math.exp(-risk)))
        rows.append({"work_order": f"WO{index:05d}", "age": age, "seniority": seniority,
                     "alerts": alerts, "days_since_service": days,
                     "usage": round(usage, 3), "late": late})
    return rows

