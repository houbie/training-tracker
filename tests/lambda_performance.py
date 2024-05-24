import os
import shutil
import subprocess
from time import sleep

import requests

url = os.environ["API_URL"]

# for version in range(15, 20):
#     print(f"Testing layer version {version}...")
#     subprocess.run(
#         [
#             shutil.which("aws"),
#             "lambda",
#             "update-function-configuration",
#             "--function-name",
#             "api-lambdaV1a",
#             "--layers",
#             f'["arn:aws:lambda:eu-west-1:525171591590:layer:TrainingTrackerApiV1apythonlibsD7DFC0ED:{version}"]',
#         ],
#         env={"AWS_PROFILE": "training-tracker", "AWS_REGION": "eu-west-1"},
#         check=True,
#         stdout=subprocess.DEVNULL,
#     )
#     sleep(20)
#     durations = []
#     for i in range(10):
#         subprocess.run(
#             [
#                 shutil.which("aws"),
#                 "lambda",
#                 "update-function-configuration",
#                 "--function-name",
#                 "api-lambdaV1a",
#                 "--environment",
#                 '{"Variables": {"TRAINING_SESSIONS_TABLE": "training-sessions-V1a",'
#                 '"POWERTOOLS_SERVICE_NAME": "ApiLambda",'
#                 f'"foo": "bar{i}",'
#                 '"ENVIRONMENT": "V1a","LOG_LEVEL": "INFO"}}',
#             ],
#             env={"AWS_PROFILE": "training-tracker", "AWS_REGION": "eu-west-1"},
#             check=True,
#             stdout=subprocess.DEVNULL,
#         )
#         durations.append(requests.get(f"{url}/training-session").elapsed.total_seconds())
#
#     print(f"average: {sum(durations) / len(durations)}, min:{min(durations)}, max:{max(durations)}")


stats = {
    "layer-default-pip-install": {
        "total": {"average": 1574.0332000000001, "min": 1499.355, "max": 1724.432},
        "durations": [
            (519.98, 745.54),
            (502.42, 736.01),
            (516.39, 738.14),
            (542.69, 705.32),
            (522.16, 719.37),
            (512.48, 710.84),
            (506.52, 699.54),
            (525.35, 749.21),
            (535.45, 710.13),
            (525.29, 713.83),
        ],
    },
    "layer-without-pycache": {
        "total": {"average": 2838.52, "min": 2754.567, "max": 3008.637},
        "durations": [
            (1078.54, 1544.86),
            (1033.83, 1424.91),
            (1061.69, 1503.21),
            (1040.66, 1529.63),
            (1025.02, 1504.29),
            (1023.20, 1482.70),
            (1046.23, 1473.14),
            (1028.23, 1456.34),
            (1047.38, 1531.45),
            (1024.65, 1451.90),
        ],
    },
    "layer-optimized-pyc": {
        "total": {"average": 2937.1487000000003, "min": 2762.688, "max": 3211.506},
        "durations": [
            (1055.07, 1459.59),
            (1098.06, 1539.48),
            (1033.50, 1495.26),
            (1110.93, 1561.82),
            (1026.83, 1444.53),
            (1090.36, 1510.63),
            (1064.30, 1541.45),
            (995.77, 1398.63),
            (1078.24, 1523.66),
            (1206.60, 1658.86),
        ],
    },
    "layer-pyc-only": {
        "total": {"average": 1491.4158, "min": 1433.314, "max": 1593.725},
        "durations": [
            (505.21, 685.63),
            (515.26, 754.72),
            (505.00, 703.70),
            (508.15, 706.73),
            (499.58, 690.32),
            (470.36, 661.09),
            (500.57, 666.39),
            (473.96, 669.78),
            (521.72, 687.40),
            (517.29, 688.11),
        ],
    },
    "layer-without-aws-sdk": {
        "total": {"average": 1483.8438999999999, "min": 1385.257, "max": 1651.21},
        "durations": [
            (478.84, 717.40),
            (481.01, 716.59),
            (479.90, 741.88),
            (458.61, 720.55),
            (459.84, 755.26),
            (460.23, 752.94),
            (433.74, 676.65),
            (467.35, 723.46),
            (479.46, 728.23),
            (440.35, 726.46),
        ],
    },
}

print(
    "Layer\tInit Avg\tInit Min\tInit Max\tDuration Avg\tDuration Min\tDuration Max\t"
    "Request Avg\tRequest Min\tRequest Max"
)
for layer, stats in stats.items():
    durations = [d[0] for d in stats["durations"]]
    init_durations = [d[1] for d in stats["durations"]]
    stats["init-duration"] = {
        "average": sum(init_durations) / len(init_durations),
        "min": min(init_durations),
        "max": max(init_durations),
    }
    stats["duration"] = {"average": sum(durations) / len(durations), "min": min(durations), "max": max(durations)}
    print(f"{layer}\t", end="")
    for key in ["init-duration", "duration", "total"]:
        print(f"{stats[key]['average']:.0f}\t{stats[key]['min']:.0f}\t{stats[key]['max']:.0f}\t", end="")
    print()

# Layer	Init Avg	Init Min	Init Max	Duration Avg	Duration Min	Duration Max	Request Avg	Request Min	Request Max
# layer-default-pip-install	723	700	749	521	502	543	1574	1499	1724
# layer-without-pycache	1490	1425	1545	1041	1023	1079	2839	2755	3009
# layer-optimized-pyc	1513	1399	1659	1076	996	1207	2937	2763	3212
# layer-pyc-only	691	661	755	502	470	522	1491	1433	1594
# layer-without-aws-sdk	726	677	755	464	434	481	1484	1385	1651
